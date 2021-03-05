import sys
from pathlib import Path
import textwrap
import io

import odf
from odf import text, element
from odf.opendocument import load

indent = '  '

def paragraph_wrap(out, text, **kwargs):
  kw = {'width': 79, 'break_long_words': True}
  kw.update(kwargs)
  out.writeln('\n'.join(textwrap.wrap(text, **kw)))
  out.write('\n')


def directive_wrap(out, text, **kwargs):
  kw = {'subsequent_indent': indent}
  kw.update(kwargs)
  paragraph_wrap(out, text, **kw)


def code(out, lines):
  out.writeln('::\n')
  for line in lines:
    out.writeln('   ', line)
  out.writeln('')


def get_header(title, level):
  header_levels = {
    0: '#',
    1: '*',
    2: '=',
    3: '-',
    4: '^',
    5: '"',
  }
  header_line = header_levels[level] * len(title)
  rv = title + '\n' + header_line + '\n'
  if level <= 1:
    rv = header_line + '\n' + rv
  if level >= 1:
    rv = '\n' + rv
  return rv + '\n'


def convert_table(rows, out):
  # Get Column Count
  col_count = None
  for row in rows:
    count = len(row)
    if col_count is None:
      col_count = count
    elif count != col_count:
      sys.exit('Invalid Table')

  # Split Lines in Cells, Get Max Row Height
  row_max = []
  for row in rows:
    max_height = 0
    for cell_i, cell in enumerate(row):
      lines = cell.split('\n')
      row[cell_i] = lines
      max_height = max(max_height, len(lines))
    row_max.append(max_height)

  # Add Blank Lines to Cells
  for row_i, row in enumerate(rows):
    for cell_i, cell in enumerate(row):
      row[cell_i] += [''] * (row_max[row_i] - len(cell))

  # Get Max Width of Columns
  col_max = [0] * col_count
  for row in rows:
    for i, cell in enumerate(row):
      col_max[i] = max(col_max[i], max(map(len, cell)) + 2)

  def print_row_div(header=False):
    for i in col_max:
      out.write('+' + ('=' if header else '-') * i)
    out.writeln('+')

  print_row_div()
  first = True
  for row_i, row in enumerate(rows):
    for line_i in range(0, row_max[row_i]):
      out.write('|')
      for cell_i, cell in enumerate(row):
        line = cell[line_i]
        fill = ' ' * (col_max[cell_i] - len(line) - 2)
        out.write(' {}{} |'.format(line, fill))
      out.writeln('')
    print_row_div(header=first)
    if first:
      first = False

def get_style(node):
  if node is None or node.attributes is None:
    return None
  return node.attributes.get(
    ('urn:oasis:names:tc:opendocument:xmlns:text:1.0', 'style-name'), None)

class Style:

  def check_node(self, doc, name):
    try:
      node = doc.getStyleByName(name)
    except AssertionError:
      return
    parent = node.attributes.get(
      ('urn:oasis:names:tc:opendocument:xmlns:style:1.0', 'parent-style-name'), None)
    if parent is not None:
      self.check_node(doc, parent)

    for child in node.childNodes:
      if child.qname not in self.props:
        self.props[child.qname] = dict()
      self.props[child.qname].update(child.attributes)

  def __init__(self, doc, node):
    self.props = {}
    self.monospace = False
    self.bold = False
    self.name = get_style(node)
    if self.name is None:
      return
    self.check_node(doc, self.name)

    for prop_group in self.props.values():
      font_family = prop_group.get(
        ('urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0', 'font-family'), None)
      font_name = prop_group.get(
        ('urn:oasis:names:tc:opendocument:xmlns:style:1.0', 'font-name'), None)
      if (font_family and 'mono' in font_family.lower()) or \
          (font_name and 'mono' in font_name.lower()):
        self.monospace = True

  def __bool__(self):
    return self.name is not None

  def __repr__(self):
    return '<{} monospace: {} bold: {}>'.format(
      repr(self.name), repr(self.monospace), repr(self.bold))

doc = load("../trunk/OpenDDSDevelopersGuide.odt")

# Dump ========================================================================

dump_path = Path('dump')
dump_path.mkdir(exist_ok=True)

# Dump XML
with (dump_path / 'main.xml').open('w') as f:
  buf = io.StringIO()
  doc.topnode.toXml(0, buf)
  import xml.dom.minidom
  print(xml.dom.minidom.parseString(buf.getvalue()).toprettyxml(), file=f)
  buf.close()

# Dump Nodes
def dump_node(doc, node, indent, f):
  style = get_style(node)
  print(indent + str(node.qname), file=f)
  for k, v in node.attributes.items():
    print(indent + 'ATTRIBUTE:', k, ':', v, file=f)
  child_indent = indent + '  '
  for child in node.childNodes:
    if child.nodeType == element.Node.ELEMENT_NODE:
      dump_node(doc, child, child_indent, f)
    elif child.nodeType == element.Node.TEXT_NODE:
      print(str(child), file=f)


nodes_path = dump_path / 'nodes'
with nodes_path.open('w') as f:
  dump_node(doc, doc.topnode, '', f)


# Convert =====================================================================

export_path = Path('devguide')
export_path.mkdir(exist_ok=True)

# Images
images_path = export_path / 'images'
images_path.mkdir(exist_ok=True)
for k, v in doc.Pictures.items():
  assert(v[0] == 1)
  path = images_path / Path(k).name
  if path.suffixes == ['.png']:
    path.write_bytes(v[1])

class Out:
  def __init__(self):
    self.out = None
    self.path = None
    self.pages = []

  @staticmethod
  def filename(name):
    rv = ''
    for c in name:
      if not str.isalnum(c):
        if c in (' ', '_', '-'):
          c = '_'
        else:
          continue
      rv += c.lower()
    return rv + '.rst'

  def open(self, name = None):
    self.close()
    if name is None:
      self.out = io.StringIO()
    else:
      filename = self.filename(name)
      self.pages.append((name, filename))
      self.path = export_path / filename
      self.out = self.path.open('w')

  def write(self, *args, **kwargs):
    if 'end' not in kwargs:
      kwargs['end'] = ''
    if self.out is not None:
      print(*args, **kwargs, file=self.out)

  def writeln(self, *args, **kwargs):
    if self.out is not None:
      print(*args, **kwargs, file=self.out)

  def close(self):
    if self.out is not None:
      self.out.close()
    self.out = None
    self.path = None

  def write_index(self):
    with (export_path / 'index.rst').open('w') as f:
      print('''\
########
DevGuide
########

.. toctree::
''', file=f)
      for name, filename in self.pages:
        print('  {}'.format(filename), file=f)

keep = {}

class Info:
  def __init__(self, doc):
    self.doc = doc
    self.data = []

  def push(self, **kwargs):
    self.data.append(dict(**kwargs))

  def pop(self):
    return self.data.pop()

  def set(self, **kwargs):
    self.data[-1].update(kwargs)

  def get(self, what, otherwise=None, ignore_last=True):
    if ignore_last:
      it = self.data[:-1]
    else:
      it = self.data
    for i in reversed(it):
      if what in i:
        return i[what]
    return otherwise

  def push_node_info(self, node):
    global keep
    self.push()
    self.set(node=node)
    if self.get('ignore_style', otherwise=False, ignore_last=False):
      style = None
    else:
      style = Style(self.doc, node)
    self.set(style=style)
    if style:
      for k, v in style.props.items():
        if k not in keep:
          keep[k] = {}
        for ki, vi in v.items():
          if ki not in keep[k]:
            keep[k][ki] = set()
          keep[k][ki] |= {vi}

  def style(self):
    return self.get('style', ignore_last=False)


def convert_child_nodes(info, doc, node, out):
  code_lines = []
  for child in node.childNodes:
    if child.nodeType == element.Node.ELEMENT_NODE and \
        child.qname[1] == 'p' and Style(doc, child).monospace:
      indent = None
      for grandchild in child.childNodes:
        if grandchild.nodeType == element.Node.ELEMENT_NODE and \
            grandchild.qname[1] == 's':
          indent = grandchild.attributes.get(
            ('urn:oasis:names:tc:opendocument:xmlns:text:1.0', 'c'), None)
          if indent is not None:
            break
      indent = 0 if indent is None else int(indent)
      code_lines.append(('  ' * indent) + get_text(info, doc, child))
    else:
      if code_lines:
        code(out, code_lines)
        code_lines = []
      convert_node(info, doc, child, out)
  if code_lines:
    code(out, code_lines)
    code_lines = []


def get_text(info, doc, node):
  pout = Out()
  pout.open()
  for child in node.childNodes:
    if child.nodeType == element.Node.ELEMENT_NODE:
      convert_node(info, doc, child, pout)
    elif child.nodeType == element.Node.TEXT_NODE:
      pout.write(str(child))
  rv = pout.out.getvalue()
  pout.close()
  return rv.rstrip()


def gather_table_rows(info, doc, parent_node, rows):
  for child_node in parent_node.childNodes:
    kind = child_node.qname[1]
    if kind == 'table-header-rows':
      gather_table_rows(info, doc, child_node, rows)
    elif kind == 'table-row':
      row = []
      for cell in child_node.childNodes:
        row.append(get_text(info, doc, cell))
      rows.append(row)

def convert_node(info, doc, node, out):
  if node is None:
    return
  info.push_node_info(node)

  style = info.style()
  if style:
    if style.monospace:
      out.write('``')
      info.push(ignore_style=True)
    elif style.bold:
      out.write('**')
      info.push(ignore_style=True)

  if node.nodeType == element.Node.ELEMENT_NODE:
    kind = node.qname[1]
    if kind == 'h':
      level = node.attributes.get(
        ('urn:oasis:names:tc:opendocument:xmlns:text:1.0', 'outline-level'), None)
      assert(level is not None)
      level = int(level) - 1
      name = str(node)
      if level == 0:
        out.open(name)
      out.write(get_header(name, level))
    elif kind == 'p' and style.name != "Figure":
      if style.name == 'Note':
        text = get_text(info, doc, node)[len('Note  '):]
        directive_wrap(out, '.. note:: {}\n'.format(text))
      else:
        paragraph_wrap(out, get_text(info, doc, node))
    elif kind == 'a':
      info.push(ignore_style=True)
      text = get_text(info, doc, node)
      link = node.attributes[('http://www.w3.org/1999/xlink', 'href')]
      if text == link:
        out.write(link)
      else:
        out.write('`{} <{}>`_'.format(text, link))
      info.pop()
    elif kind == 'image':
      mime = node.attributes.get(
        ('urn:org:documentfoundation:names:experimental:office:xmlns:loext:1.0', 'mime-type'), None)
      href = node.attributes.get(('http://www.w3.org/1999/xlink', 'href'), None)
      path = Path('images') / Path(href).name
      if mime == 'image/png' and href:
        out.writeln('.. image:: {}\n'.format(path))
    elif kind == 'table':
      rows = []
      gather_table_rows(info, doc, node, rows)
      convert_table(rows, out)
    else:
      convert_child_nodes(info, doc, node, out)
  elif node.nodeType == element.Node.TEXT_NODE:
    out.write(str(node))

  if style:
    if style.monospace:
      out.write('``')
      info.pop()
    elif style.bold:
      out.write('**')
      info.pop()

  info.pop()

from odf.office import Body
body = doc.getElementsByType(Body)[0]
from odf.text import Section
section = doc.getElementsByType(Section)[0]
out = Out()
convert_node(Info(doc), doc, section, out)
out.close()
out.write_index()

with (dump_path / 'styles_options').open('w') as f:
  for k, v in keep.items():
    print(k, file=f)
    for ki, vi in v.items():
      print('  -', ki, file=f)
      for i in vi:
        print('    -', i, file=f)
