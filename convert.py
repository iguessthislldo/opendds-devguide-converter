import sys
from pathlib import Path
import io

import odf
from odf import text, element
from odf.opendocument import load

indent = '  '

doc = load("../trunk/OpenDDSDevelopersGuide.odt")

# TODO:
# - Figure Links (bookmarks?)
# - Section Links
# - Footnotes

# Tasks
# - Replace Section Numbers with Names
# - Merge Installation Section with INSTALL.md
# - Proper use of inline monospace text like:
#   - Fix places where how the the OpenOffice docment cause the conversion
#     script to mess up, like the "Note" in
#     "Building With a Feature Enabled or Disabled".
#   - Find places that should be monospace, but are not.
#     Inproper Ex: "Extensions to the DDS Specification"
#     Proper ex: "Conditions"
#   - Quotes around monospace text. See "Persistence Profile" section
# - Do something about Figure 1-3 "Centralized Discovery with OpenDDS InfoRepo"

# Start of RST Helpers ========================================================

def write_code(out, lines):
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


def write_table(rows, out):
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


def write_list(items, numbered, out):
  bullet = '#. ' if numbered else '* '
  for item in items:
    out.writeln(item)


# Style =======================================================================

def style_name(node):
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
    self.italic = False
    self.name = style_name(node)
    if self.name is None:
      return
    if self.name == 'Note': # Ignore Italics on Notes
      return
    self.check_node(doc, self.name)

    for prop_group in self.props.values():
      def get_prop(prop_key):
        return prop_group.get(prop_key, '').lower()

      font_family = get_prop(
        ('urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0', 'font-family'))
      font_name = get_prop(
        ('urn:oasis:names:tc:opendocument:xmlns:style:1.0', 'font-name'))
      font_pitch = get_prop(
        ('urn:oasis:names:tc:opendocument:xmlns:style:1.0', 'font-pitch'))
      font_style =get_prop(
        ('urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0', 'font-style'))

      if 'mono' in font_family or 'mono' in font_name or 'courier' in font_name or \
          font_pitch == 'fixed':
        self.monospace = True

      if font_style == 'italic':
        self.italic = True

  def __bool__(self):
    return self.name is not None

  def __repr__(self):
    return '<{} monospace: {} bold: {} italic: {}>'.format(
      repr(self.name), repr(self.monospace), repr(self.bold), repr(self.italic))

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
def dump_node(node, indent, f):
  style = style_name(node)
  print(indent + str(node.qname), file=f)
  for k, v in node.attributes.items():
    print(indent + 'ATTRIBUTE:', k, ':', v, file=f)
  child_indent = indent + '  '
  for child in node.childNodes:
    if child.nodeType == element.Node.ELEMENT_NODE:
      dump_node(child, child_indent, f)
    elif child.nodeType == element.Node.TEXT_NODE:
      print(str(child), file=f)

def dump_node_exit(info, node, message):
  print('ERROR:', message, file=sys.stderr)
  print('This is the node the error happended on:', file=sys.stderr)
  print('=' * 80, file=sys.stderr)
  dump_node(node, '  ', sys.stderr)
  print('=' * 80, file=sys.stderr)
  print('Info stack (First item is top):', file=sys.stderr)
  for item in reversed(info.data):
    print(' -', repr(item), file=sys.stderr)
  sys.exit('Exiting')

nodes_path = dump_path / 'nodes'
with nodes_path.open('w') as f:
  dump_node(doc.topnode, '', f)


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
    self.newline_count = 0

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
    if self.out is not None:
      end = kwargs.get('end', '')
      sep = kwargs.get('sep', ' ')
      raw_string = sep.join(args) + end
      string = ''
      for c in raw_string:
        if c == '\n':
          if self.newline_count == 2:
            self.newline_count = 0
            continue
          self.newline_count += 1
        else:
          self.newline_count = 0
        string += c

      print(string, end='', file=self.out)

  def writeln(self, *args, **kwargs):
    if self.out is not None:
      self.write(*args, **kwargs, end='\n')

  def close(self):
    if self.out is not None:
      self.out.close()
    self.out = None
    self.path = None

  def write_index(self):
    with (export_path / 'index.rst').open('w') as f:
      print('''\
#################
Developer's Guide
#################

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
    if node.nodeType == element.Node.ELEMENT_NODE and node.qname[1] == 'p':
      self.set(paragraph=True)
      if self.get('paragraph'): # Are we nested?
        self.set(ignore_style=False) # If we are, then ignore prior style info
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


def convert_child_nodes(info, node, out):
  # Detect and Write Code Blocks
  code_lines = []
  for child in node.childNodes:
    if child.nodeType == element.Node.ELEMENT_NODE and \
        child.qname[1] == 'p' and Style(info.doc, child).monospace:
      indent = None
      for grandchild in child.childNodes:
        if grandchild.nodeType == element.Node.ELEMENT_NODE and \
            grandchild.qname[1] == 's':
          indent = grandchild.attributes.get(
            ('urn:oasis:names:tc:opendocument:xmlns:text:1.0', 'c'), None)
          if indent is not None:
            break
      indent = 0 if indent is None else int(indent)
      code_lines.append(('  ' * indent) + get_text(info, child))
    else:
      if code_lines:
        write_code(out, code_lines)
        code_lines = []
      convert_node(info, child, out)
  if code_lines:
    write_code(out, code_lines)
    code_lines = []


def get_text(info, node):
  pout = Out()
  pout.open()
  for child in node.childNodes:
    if child.nodeType == element.Node.ELEMENT_NODE:
      convert_node(info, child, pout)
    elif child.nodeType == element.Node.TEXT_NODE:
      pout.write(str(child))
  rv = pout.out.getvalue()
  pout.close()
  return rv.rstrip()


def gather_table_rows(info, parent_node, rows):
  for child_node in parent_node.childNodes:
    kind = child_node.qname[1]
    if kind == 'table-header-rows':
      gather_table_rows(info, child_node, rows)
    elif kind == 'table-row':
      row = []
      for cell in child_node.childNodes:
        row.append(get_text(info, cell))
      rows.append(row)
    elif kind not in ('soft-page-break', 'table-column'):
      dump_node_exit(info, child_node, 'Unexpected type in table: ' + kind)


def gather_list_items(info, parent_node, items):
  for child_node in parent_node.childNodes:
    kind = child_node.qname[1]
    if kind == 'list-item':
      items.append(get_text(info, child_node))
    else:
      dump_node_exit(info, child_node, 'not a list-item!')


outline_level = ('urn:oasis:names:tc:opendocument:xmlns:text:1.0', 'outline-level')

def has_outline_level(node):
  if node.nodeType == element.Node.ELEMENT_NODE:
    if outline_level in node.attributes:
      return True
    for child in node.childNodes:
      if has_outline_level(child):
        return True
  return False


def convert_node(info, node, out):
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
    elif style.italic:
      out.write('*')
      info.push(ignore_style=True)

  if node.nodeType == element.Node.ELEMENT_NODE:
    kind = node.qname[1]
    if kind == 'h':
      level = node.attributes.get(outline_level, None)
      if level is None:
        dump_node_exit(info, node, 'Header missing outline-level!')
      level = int(level) - 1
      name = ''
      for child in node.childNodes:
        if child.nodeType == element.Node.ELEMENT_NODE:
          child_kind = child.qname[1]
          if child_kind == 'frame':
            # Hack for "Figure 1-1  DCPS Conceptual Overview" quagmire which is
            # inside the header node for some unknown reason and otherwise
            # would get lost in in `name = str(node)``
            convert_node(info, child, out)
          elif child_kind == 'span':
            # Span is part of the title, again for no seeming reason
            name += str(child)
          elif child_kind not in ( # Make sure nothing else is in here we can't ignore
              'bookmark', 'bookmark-start', 'bookmark-end', 'span',
              'soft-page-break', 'line-break',
              'reference-mark-start', 'reference-mark-end'):
            dump_node_exit(info, node, 'Figure 1-1 Hack Assert Failed on ' + repr(child_kind))
        elif child.nodeType == element.Node.TEXT_NODE:
          name += str(child)
      if len(name) == 0:
        dump_node_exit(info, node, 'Header Name is Blank')
      if level == 0:
        out.open(name)
      out.write(get_header(name, level))

    elif kind == 's':
      # <text:s/>
      # TODO: This can have "c" attribute like: <text:s text:c="2"/>
      # Use it?
      out.write(' ')

    elif kind == 'p' and style is None:
      if style_name(node) == 'Footnote':
        # TODO this needs to be written outside a table
        pass
      else:
        dump_node_exit(info, node,
          'Paragraph style is None, style name: ' + repr(style_name(node)))

    elif kind == 'p' and style.name != "Figure":
      if style.name == 'Note':
        out.writeln('.. note:: ' + get_text(info, node)[len('Note  '):])
      else:
        text = get_text(info, node)
        if text and text[-1] != '\n' and not info.get('ignore_style', ignore_last=False):
          text += '\n\n'
        out.write(text)

    elif kind == 'a':
      info.push(ignore_style=True)
      text = get_text(info, node)
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
      gather_table_rows(info, node, rows)
      write_table(rows, out)

    elif kind == 'list':
      if has_outline_level(node):
        convert_child_nodes(info, node, out)
      elif len(node.childNodes) == 1 and node.childNodes[0].qname[1] == 'list-header':
        # Hack for a quagmire in "Policy Example"
        convert_child_nodes(info, node, out)
      else:
        # Normal Lists
        items = []
        gather_list_items(info, node, items)
        for item in items:
          out.writeln(item + '\n')

    elif kind == 'list-item':
      convert_child_nodes(info, node, out)

    else:
      passthrough = {
        # Definitely Passthrough
        'section', # ROOT OF CONTENT, VERY IMPORTANT!
        'soft-page-break',
        'line-break',
        'list-header',

        # TODO: Handle?
        'bookmark-ref',
        'sequence-ref',
        'reference-ref',
        'bookmark-start',
        'bookmark-end',
        'frame',
        'sequence',
        'note',
        'tab',
        'note-citation',
        'bookmark',
        'text-box',
        'note-body',
        'span',
        'p',
      }
      if kind in passthrough:
        convert_child_nodes(info, node, out)
      else:
        dump_node_exit(info, node, 'Unexpected tag in convert_nodes: ' + kind)

  elif node.nodeType == element.Node.TEXT_NODE:
    out.write(str(node))

  if style:
    if style.monospace:
      out.write('``')
      info.pop()
    elif style.bold:
      out.write('**')
      info.pop()
    elif style.italic:
      out.write('*')
      info.pop()

  info.pop()

from odf.office import Body
body = doc.getElementsByType(Body)[0]
from odf.text import Section
section = doc.getElementsByType(Section)[0]
out = Out()
convert_node(Info(doc), section, out)
out.close()
out.write_index()

# Dump Style Value Permutations ===============================================

with (dump_path / 'styles_options').open('w') as f:
  for k, v in keep.items():
    print(k, file=f)
    for ki, vi in v.items():
      print('  -', ki, file=f)
      for i in vi:
        print('    -', i, file=f)
