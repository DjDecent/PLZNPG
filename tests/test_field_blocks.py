"""Field-block regressions for reusable ZPL behavior."""
import unittest
from PIL import ImageChops
from zplconvert import convert_zpl_to_image
from zplconvert.parser import parse_zpl
from zplconvert.elements.field_block import FieldBlockElement



class FieldBlockTests(unittest.TestCase):
    def test_field_separator_resets_block(self):
        label = parse_zpl('^XA^FO20,20^A0N,30^FB300,1,0,C^FDHeading^FS^FO20,100^FDPlain^FS^XZ')
        self.assertIsInstance(label.elements[0], FieldBlockElement)
        self.assertNotIsInstance(label.elements[1], FieldBlockElement)
        actual = label.render().crop((0,100,400,160))
        expected = convert_zpl_to_image('^XA^FO20,100^A0N,30^FDPlain^FS^XZ').crop((0,100,400,160))
        self.assertIsNone(ImageChops.difference(actual, expected).getbbox())

    def test_left_center_right_move_text_inside_same_block(self):
        bounds = []
        for alignment in 'LCR':
            image = convert_zpl_to_image(f'^XA^FO20,20^A0N,30^FB300,1,0,{alignment}^FDTEST^FS^XZ')
            bounds.append(ImageChops.invert(image.convert('L')).getbbox())
        self.assertLess(bounds[0][0], bounds[1][0])
        self.assertLess(bounds[1][0], bounds[2][0])
        self.assertLessEqual(bounds[2][2], 320)
        self.assertEqual(len({b[2]-b[0] for b in bounds}), 1)

    def test_break_spacing_indent_and_last_line_overprint(self):
        label = parse_zpl(r'^XA^FO20,20^A0N,30^FB300,2,7,L,25^FDOne\&Two\&Three^FS^XZ')
        runs = label.elements[0].layout()
        self.assertEqual([r[0] for r in runs], ['One', 'Two', 'Three'])
        self.assertEqual([r[1] for r in runs], [0, 25, 25])
        self.assertEqual([r[2] for r in runs], [0, 37, 37])

    def test_wraps_words_and_splits_long_words(self):
        label = parse_zpl('^XA^A0N,30^FB100,10^FDONE TWO THREE ABCDEFGHIJKLMNOP^FS^XZ')
        runs = label.elements[0].layout()
        self.assertGreater(len(runs), 2)
        self.assertIn('ONE', [run[0] for run in runs])
        self.assertTrue(any(run[0].endswith('-') for run in runs))

    def test_zero_width_suppresses_text(self):
        image = convert_zpl_to_image('^XA^A0N,30^FB0^FDHidden^FS^XZ')
        self.assertIsNone(ImageChops.invert(image).getbbox())


if __name__ == '__main__':
    unittest.main()
