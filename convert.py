import sys
import os
from pathlib import Path
import io
import re

import odf
from odf import text, element
from odf.opendocument import load

doc = load(os.environ['OPENDDS_DEVGUIDE_ODT'])

# Things to fix in this script:
# - Figure Links (bookmarks?)
# - Footnotes
# - List in "Building OpenDDS with Security on Windows"
# - Replace Section Numbers with Names
# - Include the preface in the conversion
# - Images are missing?
# - More automatic code detection

# Tasks to do manually
# - Merge Installation Section with INSTALL.md
# - Proper use of inline monospace text like:
#   - Fix places where how the the OpenOffice docment cause the conversion
#     script to mess up, like the "Note" in
#     "Building With a Feature Enabled or Disabled".
#   - Find places that should be monospace, but are not.
#     Improper Ex: "Extensions to the DDS Specification"
#     Proper ex: "Conditions"
#   - Quotes around monospace text. See "Persistence Profile" section
# - Do something about Figure 1-3 "Centralized Discovery with OpenDDS InfoRepo"
# - Reword references to the words "chapter" and "section" because that doens't
# make as much sense in Sphinx, specially with the current section name link
# insertion.

# One Sentence per Line =======================================================

import nltk

nltk.download('punkt')

import nltk.data

sentence_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

def one_sentence_per_line(text, indent_following_lines=''):
  lines = []
  for line in sentence_tokenizer.tokenize(text):
    if indent_following_lines and lines:
      line = indent_following_lines + line
    lines.append(line)
  return '\n'.join(lines)


# RST Helpers =================================================================

code_regex = {
  'omg-idl': re.compile(r'@key|@topic|module DDS|interface|enum|boolean|struct'),
  'ini': re.compile('\[common]|\[transport|\[domain|\[config'),
  'xml': re.compile('xml version="1.0"'),
  'cpp': re.compile('int main|#include.*\.h[">]|int ACE_TMAIN|_var |OpenDDS::DCPS::|std::|\w->'),
  'java': re.compile('public static void main|System.out.println|Helper|null'),
  'bash': re.compile('\$(ACE|DDS)'),
  'doscon': re.compile('\%(ACE|DDS)'),
  'mpc': re.compile('project[\(:]'),
}
def write_code(out, lines):
  # Detect
  code = '\n'.join(lines)
  names = []
  for name, regex in code_regex.items():
    if regex.search(code):
      names.append(name)
  # if None not in names:
  #   if len(names) == 0:
  #     print('Could not find name for:')
  #     print('=' * 80)
  #     print(code)
  #     print('=' * 80)
  name = None
  if names:
    if len(names) > 1:
      print('Matched more than one name for code:', ', '.join(names), file=sys.stderr)
      print('=' * 80, file=sys.stderr)
      print(code, file=sys.stderr)
      print('=' * 80, file=sys.stderr)
      sys.exit(1)
    name = names[0]

  # Write
  if name is None:
    out.writeln('::\n')
  else:
    out.writeln('.. code-block:: {}\n'.format(name))
  for line in lines:
    if line:
      out.write('   ', line)
    out.write('\n')

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


def fix_monospace(raw_string, last_char_arg=None):
  tick_count = 0
  string = ''
  keep_back = None
  state = 0
  for c in raw_string:
    last_char = string[-1] if string else last_char_arg
    if c == '`':
      if state == 0: # Left of ``..``
        if tick_count == 1: # Almost Inside ``..``
          if last_char and last_char.isalnum():
            string += ' '
          string += '``'
          state = 1
          tick_count = 0
        else:
          tick_count += 1
        continue
      elif state == 1: # Inside ``..``
        if tick_count == 1: # Almost Outside ``..``
          keep_back = '``'
          state = 2
          tick_count = 0
        else:
          tick_count += 1
        continue
      elif state == 2: # After ``..``
        if tick_count == 1: # Almost Outside ``..``
          tick_count = 0
          keep_back = None
          state = 1
        else:
          tick_count += 1
        continue
    else:
      if state == 2: # After ``
        string += keep_back
        keep_back = None
        if c.isalnum():
          string += ' '
        state = 0
      else:
        if keep_back:
          string += keep_back
          keep_back = None
        string += '`' * tick_count
        tick_count = 0
    string += c
  if keep_back:
    string += keep_back
  if tick_count:
    string += '`' * tick_count
  return string


def write_table(rows, out):
  new_rows = []
  for row in rows:
    new_row = []
    for cell in row:
      new_row.append(fix_monospace(cell))
    new_rows.append(new_row)
  rows = new_rows

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

  out.writeln('')


def write_list(list_info, out):
  bullet = '#. ' if list_info['numbered'] else '* '
  indent = ' ' * len(bullet)
  for item in list_info['items']:
    if item:
      out.writeln(bullet + item[0])
      for line in item[1:]:
        if line:
          out.write(indent)
        out.writeln(line)
      out.writeln('')
  out.writeln('')


def inline_markup(string, what):
  if len(string) == 0:
    return ''
  return '{0}{1}{0}'.format(
    {
     'monospace': '``',
     'italic': '*',
     'bold': '**',
    }[what], string.strip())


def paragraph_break(text):
  rv = text
  if len(text) > 0 and not text.endswith('\n\n'):
    if text.endswith('\n'):
      rv += '\n'
    else:
      rv += '\n\n'
  return rv


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

  def __init__(self, info, node=None, name=None):
    self.props = {}
    self.inline = None
    if node is None != name is None:
      raise ValueError('Invalid Arguments')
    self.name = style_name(node) if node is not None else name
    if self.name is None:
      return
    if self.name == 'Note': # Ignore Italics on Notes
      return
    self.check_node(info.doc, self.name)

    for prop_group in self.props.values():
      def get_prop(prop_key):
        return prop_group.get(prop_key, '').lower()

      font_family = get_prop(
        ('urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0', 'font-family'))
      font_name = get_prop(
        ('urn:oasis:names:tc:opendocument:xmlns:style:1.0', 'font-name'))
      font_pitch = get_prop(
        ('urn:oasis:names:tc:opendocument:xmlns:style:1.0', 'font-pitch'))
      font_style = get_prop(
        ('urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0', 'font-style'))
      font_style_name = get_prop(
        ('urn:oasis:names:tc:opendocument:xmlns:style:1.0', 'font-style-name'))
      font_weight = get_prop(
        ('urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0', 'font-weight'))

      if font_style == 'italic':
        self.inline = 'italic'

      if 'bold' in (font_style_name, font_weight):
        self.inline = 'bold'

      if 'mono' in font_family or 'mono' in font_name or 'courier' in font_name or \
          font_pitch == 'fixed':
        self.inline = 'monospace'

    if node and node.nodeType == element.Node.ELEMENT_NODE and node.qname[1] == 'h':
      self.inline = None

  def __bool__(self):
    return self.name is not None

  def __repr__(self):
    return '<{} inline={}>'.format(repr(self.name), repr(self.inline))

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
    self.keep_back = None
    self.tilde_count = 0
    self.inline_monospace_state = 0
    self.last_char = None

  @staticmethod
  def filename(name, ext='.rst'):
    rv = ''
    for c in name:
      if not str.isalnum(c):
        if c in (' ', '_', '-'):
          c = '_'
        else:
          continue
      rv += c.lower()
    return rv + ext

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
      if self.path:
        string = ''
        for c in raw_string:
          last_char = string[-1] if string else self.last_char
          if c == '\n':
            if self.keep_back:
              string += self.keep_back
              self.keep_back = None
            string += '`' * self.tilde_count
            self.tilde_count = 0
            self.inline_monospace_state = 0
            if self.newline_count == 2:
              self.newline_count = 0
              continue
            self.newline_count += 1
          elif c == '`':
            self.newline_count = 0
            if self.inline_monospace_state == 0: # Left of ``..``
              if self.tilde_count == 1: # Almost Inside ``..``
                if last_char.isalnum():
                  string += ' '
                string += '``'
                self.inline_monospace_state = 1
                self.tilde_count = 0
              else:
                self.tilde_count += 1
              continue
            elif self.inline_monospace_state == 1: # Inside ``..``
              if self.tilde_count == 1: # Almost Outside ``..``
                self.keep_back = '``'
                self.inline_monospace_state = 2
                self.tilde_count = 0
              else:
                self.tilde_count += 1
              continue
            elif self.inline_monospace_state == 2: # After ``..``
              if self.tilde_count == 1: # Almost Outside ``..``
                self.tilde_count = 0
                self.keep_back = None
                self.inline_monospace_state = 1
              else:
                self.tilde_count += 1
              continue
          else:
            if self.inline_monospace_state == 2: # After ``
              string += self.keep_back
              self.keep_back = None
              if c.isalnum():
                string += ' '
              self.inline_monospace_state = 0
            else:
              if self.keep_back:
                string += self.keep_back
                self.keep_back = None
              string += '`' * self.tilde_count
              self.tilde_count = 0
            self.newline_count = 0
          string += c
      else:
        string = raw_string

      if string:
        self.last_char = string[-1]
      print(string, end='', file=self.out)

  def writeln(self, *args, **kwargs):
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

  def __repr__(self):
    return '<Out: ' + (str(self.path) if self.path is not None else 'BUFFER') + '>'


class Info:
  def __init__(self, doc, sections=None):
    self.doc = doc
    self.data = []
    self.all_style_prop_groups = {}
    if sections is None:
      self.sections = {}
      self.push(section_level=0, section_number=0, section_id="")
    else:
      self.sections = sections
    self.bookmarks = {}

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
    self.push()
    self.set(node=node)
    style = None
    if node.nodeType == element.Node.ELEMENT_NODE and node.qname[1] == 'p':
      if style_name(node) == 'P209':
        style = Style(self, name='Note')
      self.set(paragraph=True)
      if self.get('paragraph'): # Are we nested?
        self.set(ignore_style=False) # If we are, then ignore prior style info
    if self.get('ignore_style', otherwise=False, ignore_last=False):
      style = None
    elif style is None:
      style = Style(self, node)
    self.set(style=style)
    if style:
      if style.inline is not None:
        self.set(ignore_style=True)
      # Save Style Options
      for k, v in style.props.items():
        if k not in self.all_style_prop_groups:
          self.all_style_prop_groups[k] = {}
        for ki, vi in v.items():
          if ki not in self.all_style_prop_groups[k]:
            self.all_style_prop_groups[k][ki] = set()
          self.all_style_prop_groups[k][ki] |= {vi}

  def style(self):
    return self.get('style', ignore_last=False)


def convert_child_nodes(info, node, out):
  # Detect and Write Code Blocks
  code_lines = []
  for child in node.childNodes:
    if child.nodeType == element.Node.ELEMENT_NODE and \
        child.qname[1] == 'p' and Style(info, child).inline == 'monospace':
      info.push(ignore_style=True)
      indent = None
      for grandchild in child.childNodes:
        if grandchild.nodeType == element.Node.ELEMENT_NODE and \
            grandchild.qname[1] == 's':
          indent = grandchild.attributes.get(
            ('urn:oasis:names:tc:opendocument:xmlns:text:1.0', 'c'), None)
          if indent is not None:
            break
      line = get_text(info, child)
      if indent and line:
        line = ' ' * int(indent) + line.strip()
      code_lines.append(line)
      info.pop()
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


start_value = ('urn:oasis:names:tc:opendocument:xmlns:text:1.0', 'start-value')

def gather_list_items(info, parent_node):
  list_level = info.get('list_level', 0, ignore_last=False)
  list_level += 1
  info.push(list_level=list_level)
  rv = dict(numbered=False, items=[])
  for child_node in parent_node.childNodes:
    kind = child_node.qname[1]
    if kind == 'list-item':
      if start_value in child_node.attributes:
        rv['numbered'] = True
      rv['items'].append(get_text(info, child_node).split('\n'))
    else:
      dump_node_exit(info, child_node, 'not a list-item!')
  info.pop()
  return rv


outline_level = ('urn:oasis:names:tc:opendocument:xmlns:text:1.0', 'outline-level')

def has_outline_level(node):
  if node.nodeType == element.Node.ELEMENT_NODE:
    if outline_level in node.attributes:
      return True
    for child in node.childNodes:
      if has_outline_level(child):
        return True
  return False


def handle_header(info, node, out=None):
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
        if out:
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

  if out: # in convert_node
    if level == 0:
      out.open(name)
    out.write(get_header(name, level))

  else: # in reference_builder
    level += 1
    section_level = info.get('section_level', ignore_last=False)
    section_number = info.get('section_number', ignore_last=False)
    section_id = info.get('section_id', ignore_last=False)
    if level > section_level:
      if section_number > 0:
        section_id += str(section_number) + "."
      section_number = 1
      info.push(section_level=level, section_id=section_id, section_number=section_number)
    elif level < section_level:
      for i in range(section_level - level):
        info.pop()
      section_number = info.get('section_number', ignore_last=False) + 1
      info.set(section_number=section_number)
    else:
      section_number = info.get('section_number', ignore_last=False) + 1
      info.set(section_number=section_number)
    section_id = info.get('section_id', ignore_last=False) + str(section_number)
    if level == 1:
      info.set(section_filename=Out.filename(name, ext=''))
    info.sections[section_id] = dict(
      name=name, filename=info.get('section_filename', ignore_last=False))


def reference_builder(info, node):
  if node is None:
    return
  if node.nodeType == element.Node.ELEMENT_NODE:
    kind = node.qname[1]
    if kind == 'h':
      handle_header(info, node)
    for child_node in node.childNodes:
      reference_builder(info, child_node)


def convert_node(info, node, out):
  if node is None:
    return
  info.push_node_info(node)
  style = info.style()
  inline = style.inline if style is not None else None
  real_out = out
  if inline:
    out = Out()
    out.open()

  if node.nodeType == element.Node.ELEMENT_NODE:
    kind = node.qname[1]

    if kind == 'h':
      handle_header(info, node, out)

    elif kind == 's':
      # <text:s/>
      # TODO: This can have "c" attribute like: <text:s text:c="2"/>
      # Use it?
      out.write(' ')

    # TODO: One of the problems with this is "Table 7-7 [datawriterqos/*] Configuration Options"
    # Can inserts newlines into monospaced lines
    # elif kind == 'line-break':
    #   out.writeln('')

    elif kind == 'p' and style is None:
      if style_name(node) == 'Footnote':
        # TODO this needs to be written outside a table
        pass
      else:
        dump_node_exit(info, node,
          'Paragraph style is None, style name: ' + repr(style_name(node)))

    elif kind == 'p' and style.name != "Figure":
      raw_text = get_text(info, node)
      if raw_text != 'Note':
        indent = ''
        if style.name == 'Note':
          if 'ecurity/certs/identity/identity_ca_openssl.cnf' in raw_text:
            raw_text = '  ' + raw_text
          else:
            raw_text = '.. note:: ' + raw_text
            indent = '  '
        text = one_sentence_per_line(raw_text, indent)
        if not inline:
          text = paragraph_break(text)
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
        write_list(gather_list_items(info, node), out)

    elif kind == 'list-item':
      convert_child_nodes(info, node, out)

    elif kind in ('bookmark-start'):
      name = node.attributes[('urn:oasis:names:tc:opendocument:xmlns:text:1.0', 'name')]
      if not name.startswith('__RefHeading'): # Ignore Heading
        if name in info.bookmarks:
          dump_node_exit(info, node, 'bookmark already in bookmarks: ' + kind)
        info.bookmarks[name] = '_bookmark' + name

    elif kind in ('bookmark-ref', 'sequence-ref', 'reference-ref'):
      reference_format_attr = ('urn:oasis:names:tc:opendocument:xmlns:text:1.0', 'reference-format')
      reference_formats = ("category-and-value", "chapter", "number", "number-all-superior", "page", "text")
      reference_format = node.attributes.get(reference_format_attr, None)
      value = get_text(info, node)
      if not value.isspace():
        value = value.strip()
      if value:
        if kind in ('bookmark-ref', 'reference-ref') and reference_format in ('chapter', 'number'):
          odf_ref_name = node.attributes[('urn:oasis:names:tc:opendocument:xmlns:text:1.0', 'ref-name')]
          # print(kind, reference_format, value, odf_ref_name)
          if reference_format == 'chapter' or odf_ref_name.startswith('__RefHeading'):
            section_info = info.sections[value.strip()]
            out.write(':ref:`{}`'.format(section_info['name']))
          else:
            out.write(':ref:`{} <{}>`'.format(value, info.bookmarks[odf_ref_name]))
        else:
          # print(kind, reference_format, value)
          convert_child_nodes(info, node, out)

    else:
      passthrough = {
        'section', # ROOT OF CONTENT, VERY IMPORTANT!
        'list-header',
        'line-break', # TODO, see above

        # TODO: Handle?
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
        'soft-page-break',
      }
      if kind in passthrough:
        convert_child_nodes(info, node, out)
      else:
        dump_node_exit(info, node, 'Unexpected tag in convert_nodes: ' + kind)

  elif node.nodeType == element.Node.TEXT_NODE:
    out.write(str(node))

  if inline:
    lines = []
    for line in out.out.getvalue().split('\n'):
      if not line.startswith('.. image::'):
        line = inline_markup(line, inline)
      lines.append(line)
    rv = '\n'.join(lines)
    if kind == 'p':
      rv = paragraph_break(rv)
    out.close()
    real_out.write(rv)

  info.pop()

from odf.office import Body
body = doc.getElementsByType(Body)[0]
from odf.text import Section
section = doc.getElementsByType(Section)[0]

ref_info = Info(doc)
reference_builder(ref_info, section)
with (dump_path / 'sections').open('w') as f:
  for section_id, section_info in ref_info.sections.items():
    print(section_id, repr(section_info['name']), repr(section_info['filename']), file=f)

out = Out()
info = Info(doc, ref_info.sections)
convert_node(info, section, out)
out.close()
out.write_index()

# Dump Style Value Permutations ===============================================

with (dump_path / 'styles_options').open('w') as f:
  for prop_group_key in sorted(info.all_style_prop_groups):
    print(prop_group_key, file=f)
    prop_group = info.all_style_prop_groups[prop_group_key]
    for prop_key in sorted(prop_group):
      print('  -', prop_key, file=f)
      prop = prop_group[prop_key]
      for prop_value in sorted(prop):
        print('    -', prop_value, file=f)
