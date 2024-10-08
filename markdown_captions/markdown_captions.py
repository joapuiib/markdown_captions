# Evan Widloski - 2019-04-18
# python-markdown extension for captions

from __future__ import absolute_import
from __future__ import unicode_literals
from markdown.extensions import Extension
from markdown.inlinepatterns import LinkInlineProcessor, ReferenceInlineProcessor
from markdown.inlinepatterns import IMAGE_REFERENCE_RE
from markdown.extensions.attr_list import AttrListTreeprocessor
import re
from xml.etree import ElementTree

# CAPTION_RE1 = r'\!\['
CAPTION_RE = r'\!\[(?=[^\]])'

# handle regular inline image: ![caption](img.jpg)
# with multiple captions support: ![caption1][caption2](img.jpg)
class ImageInlineProcessor(LinkInlineProcessor):

    BRACKET_RE = re.compile(r'\[\s*(.*?)\s*\]')
    # Modified original AttrListTreeprocessor.BASE_RE
    # so it isn't greedy [^\n]*? and allows
    # looking for multiple attr_list in the same line
    ATTR_LIST_RE = re.compile(r'\{\:?[ ]*([^\}\n ][^\n]*?)[ ]*\}') # 

    def handleMatch(self, m, data):
        captions = []
        looking_for_captions = True
        index = m.end(0) - 1

        while looking_for_captions:
            text, text_index, handled = self.getText(data, index + 1)

            if handled:
                index = text_index

                # find caption attr_list
                curly = None
                if 'attr_list' in self.md.treeprocessors:
                    # find attr_list curly braces
                    curly = re.match(self.ATTR_LIST_RE, data[index:])
                    if curly:
                        # remove original '{: xxx}'
                        index += curly.end()

                if text:
                    captions.append((text, curly))
            else:
                looking_for_captions = False

        if not captions:
            return None, None, None

        src, title, index, handled = self.getLink(data, index)
        if not handled:
            return None, None, None

        fig = ElementTree.Element('figure')
        img = ElementTree.SubElement(fig, 'img')

        img.set('src', src)
        if title is not None:
            img.set("title", title)

        # Add captions to figure
        for caption in captions:
            cap = ElementTree.SubElement(fig, 'figcaption')
            cap.text = caption[0]

            # Put '{: xxx} at the end <figcaption> so attr_list will see it
            if caption[1] and 'attr_list' in self.md.treeprocessors:
                cap.text += '\n'
                cap.text += caption[1].group()


        # if attr_list is enabled, put '{: xxx}' inside <figure> at end
        # so attr_list will see it
        if 'attr_list' in self.md.treeprocessors:
            # find attr_list curly braces
            curly = re.match(AttrListTreeprocessor.BASE_RE, data[index:])
            if curly:
                fig[-1].tail = '\n'
                fig[-1].tail += curly.group()
                # remove original '{: xxx}'
                index += curly.end()

        return fig, m.start(0), index

# handle image with reference:
#   ![caption][ref]
#   [ref]: img.jpg
class ImageReferenceInlineProcessor(ReferenceInlineProcessor):
    """ Match to a stored reference and return img element. """
    def makeTag(self, href, title, text):
        fig = ElementTree.Element('figure')
        img = ElementTree.SubElement(fig, 'img')
        cap = ElementTree.SubElement(fig, 'figcaption')

        img.set("src", href)

        if title is not None:
            img.set("title", title)

        cap.text = self.unescape(text)
        #
        # if attr_list is enabled, put '{: xxx}' inside <figure> at end
        # so attr_list will see it
        if 'attr_list' in self.md.treeprocessors:
            # find attr_list curly braces
            curly = re.match(AttrListTreeprocessor.BASE_RE, data[index:])
            if curly:
                fig[-1].tail = '\n'
                fig[-1].tail += curly.group()
                # remove original '{: xxx}'
                index += curly.end()


        return fig
    def handleMatch(self, m, data):
        text, index, handled = self.getText(data, m.end(0))
        if not handled:
            return None, None, None

        id, index, handled = self.evalId(data, index, text)
        if not handled:
            return None, None, None

        # Clean up linebreaks in id
        id = self.NEWLINE_CLEANUP_RE.sub(' ', id)
        if id not in self.md.references:  # ignore undefined refs
            return None, m.start(0), index

        href, title = self.md.references[id]

        # ----- build element -----

        fig = ElementTree.Element('figure')
        img = ElementTree.SubElement(fig, 'img')
        cap = ElementTree.SubElement(fig, 'figcaption')

        img.set("src", href)

        if title is not None:
            img.set("title", title)

        cap.text = self.unescape(text)

        # if attr_list is enabled, put '{: xxx}' inside <figure> at end
        # so attr_list will see it
        if 'attr_list' in self.md.treeprocessors:
            # find attr_list curly braces
            curly = re.match(AttrListTreeprocessor.BASE_RE, data[index:])
            if curly:
                fig[-1].tail = '\n'
                fig[-1].tail += curly.group()
                # remove original '{: xxx}'
                index += curly.end()

        return fig, m.start(0), index


# handle image with short reference:
#   ![caption]
#   [caption]: img.jpg
class ShortImageReferenceInlineProcessor(ImageReferenceInlineProcessor):
    """ Short form of inage reference: ![ref]. """
    def evalId(self, data, index, text):
        """Evaluate the id from of [ref]  """

        return text.lower(), index, True


# ---------- Extension Registration ----------

class CaptionsExtension(Extension):
    def extendMarkdown(self, md):
        md.inlinePatterns.register(ImageInlineProcessor(CAPTION_RE, md), 'caption', 161)
        md.inlinePatterns.register(ImageReferenceInlineProcessor(CAPTION_RE, md), 'ref_caption', 151)
        md.inlinePatterns.register(ShortImageReferenceInlineProcessor(CAPTION_RE, md), 'short_ref_caption', 151)


def makeExtension(**kwargs):
    return CaptionsExtension(**kwargs)
