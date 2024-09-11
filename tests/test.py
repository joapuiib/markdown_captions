import unittest
import markdown

class Tests(unittest.TestCase):

    def test_captions(self):
        md = markdown.Markdown(extensions=['markdown_captions'])

        # no caption img
        self.assertEqual(
            md.convert('![](foo.png)'),
            '<p><img alt="" src="foo.png" /></p>'
        )

        # FIXME: dont want newline before closing figure tag

        # captioned img
        self.assertEqual(
            md.convert('![caption](foo.png)'),
            '<p>\n<figure><img src="foo.png" /><figcaption>caption</figcaption>\n</figure>\n</p>'
        )

        # title
        self.assertEqual(
            md.convert('![caption](foo.png "title")'),
            '<p>\n<figure><img src="foo.png" title="title" /><figcaption>caption</figcaption>\n</figure>\n</p>'
        )

        # referenced image
        self.assertEqual(
            md.convert('![caption][ref]\n[ref]: foo.png'),
            '<p>\n<figure><img src="foo.png" /><figcaption>caption</figcaption>\n</figure>\n</p>'
        )

        # no caption referenced image
        self.assertEqual(
            md.convert('![][ref]\n[ref]: foo.png'),
            '<p><img alt="" src="foo.png" /></p>'
        )

        # short referenced image
        self.assertEqual(
            md.convert('![caption]\n[caption]: foo.png'),
            '<p>\n<figure><img src="foo.png" /><figcaption>caption</figcaption>\n</figure>\n</p>'
        )

    def test_captions_attr(self):
        md = markdown.Markdown(extensions=['markdown_captions', 'attr_list'])

        # no caption img w/ attr_list
        self.assertEqual(
            md.convert('![](foo.png){: .class}'),
            '<p><img alt="" class="class" src="foo.png" /></p>'
        )

        # captioned img w/ attr_list
        self.assertEqual(
            md.convert('![caption](foo.png){: .class}'),
            '<p>\n<figure class="class"><img src="foo.png" /><figcaption>caption</figcaption></figure>\n</p>'
        )
        # captioned img w/ attr_list
        self.assertEqual(
            md.convert('![caption](foo.png){: .class}\n![caption2](foo2.png){: .class2}'),
            (
                '<p>\n<figure class="class"><img src="foo.png" /><figcaption>caption</figcaption></figure>'
                + '\n<figure class="class2"><img src="foo2.png" /><figcaption>caption2</figcaption></figure>\n</p>'

            )
        )

        # referenced image w/ attr_list
        self.assertEqual(
            md.convert('![caption][ref]{: .class}\n[ref]: foo.png'),
            '<p>\n<figure class="class"><img src="foo.png" /><figcaption>caption</figcaption></figure>\n</p>'
        )

        # short referenced image w/ attr_list
        self.assertEqual(
            md.convert('![caption]{: .class}\n[caption]: foo.png'),
            '<p>\n<figure class="class"><img src="foo.png" /><figcaption>caption</figcaption></figure>\n</p>'
        )

    def test_multiple_captions(self):
        md = markdown.Markdown(extensions=['markdown_captions'])

        # two captioned img
        self.assertEqual(
            md.convert('![caption1][caption2](foo.png)'),
            '<p>\n<figure><img src="foo.png" /><figcaption>caption1</figcaption>\n<figcaption>caption2</figcaption>\n</figure>\n</p>'
        )

        # three captioned img
        self.assertEqual(
            md.convert('![caption1][caption2][caption3](foo.png)'),
            '<p>\n<figure><img src="foo.png" /><figcaption>caption1</figcaption>\n<figcaption>caption2</figcaption>\n<figcaption>caption3</figcaption>\n</figure>\n</p>'
        )

    def test_multiple_captions_attr(self):
        md = markdown.Markdown(extensions=['markdown_captions', 'attr_list'])

        # multiple captions but only first classed
        self.assertEqual(
            md.convert('![caption]{: .class}(foo.png)'),
            '<p>\n<figure><img src="foo.png" /><figcaption class="class">caption</figcaption>\n</figure>\n</p>'
        )

        # multiple captions but only second classed
        self.assertEqual(
            md.convert('![caption]{: .class}[caption2](foo.png)'),
            '<p>\n<figure><img src="foo.png" /><figcaption class="class">caption</figcaption>\n<figcaption>caption2</figcaption>\n</figure>\n</p>'
        )

        # multiple classed captions img
        self.assertEqual(
            md.convert('![caption]{: .class}[caption2]{: .class2}(foo.png)'),
            '<p>\n<figure><img src="foo.png" /><figcaption class="class">caption</figcaption>\n<figcaption class="class2">caption2</figcaption>\n</figure>\n</p>'
        )

        # multiple classed captions and classed figure
        self.assertEqual(
                md.convert('![caption]{: .class}[caption2]{: .class2}(foo.png){: #figure}'),
            '<p>\n<figure id="figure"><img src="foo.png" /><figcaption class="class">caption</figcaption>\n<figcaption class="class2">caption2</figcaption></figure>\n</p>'
        )


if __name__ == '__main__':
    unittest.main()
