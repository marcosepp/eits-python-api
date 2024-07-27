import unittest

from eits_python_api.common import (
    add_colon_before_first_whitespace,
    remove_tab_and_text_after_tab,
    remove_html_tags,
    remove_whitespace_and_text_after_whitespace,
    get_group_name,
    get_risks,
)


class TestRemoveHtmlTags(unittest.TestCase):
    def test_remove_html_tags_with_valid_input(self):
        self.assertEqual(
            "Hello World", remove_html_tags("<p>Hello <b>World</b></p>")
        )

    def test_remove_html_tags_with_invalid_input(self):
        with self.assertRaises(TypeError):
            remove_html_tags({"key": "value"})

    def test_remove_html_tags_with_empty_string(self):
        self.assertEqual("", remove_html_tags(""))

    def test_remove_html_tags_with_none(self):
        with self.assertRaises(TypeError):
            remove_html_tags(None)

    def test_remove_html_tags_with_int(self):
        with self.assertRaises(TypeError):
            remove_html_tags(123)


class TestFixTitles(unittest.TestCase):
    pass


class TestAddColonBeforeFirstWhitespace(unittest.TestCase):
    def test_add_colon_before_first_whitespace_with_valid_input(self):
        self.assertEqual(
            "Hello: World", add_colon_before_first_whitespace("Hello World")
        )

    def test_add_colon_before_first_whitespace_with_invalid_input(self):
        with self.assertRaises(TypeError):
            add_colon_before_first_whitespace({"key": "value"})

    def test_add_colon_before_first_whitespace_with_empty_string(self):
        self.assertEqual(": ", add_colon_before_first_whitespace(""))

    def test_add_colon_before_first_whitespace_with_none(self):
        with self.assertRaises(TypeError):
            add_colon_before_first_whitespace(None)


class TestRemoveTabAndTextAfterTab(unittest.TestCase):
    def test_remove_tab_and_text_after_tab_with_valid_input(self):
        self.assertEqual("Asd", remove_tab_and_text_after_tab("Asd\tHello"))

    def test_remove_tab_and_text_after_tab_with_invalid_input(self):
        with self.assertRaises(TypeError):
            remove_tab_and_text_after_tab({"key": "value"})

    def test_remove_tab_and_text_after_tab_with_empty_string(self):
        self.assertEqual("", remove_tab_and_text_after_tab("\t"))

    def test_remove_tab_and_text_after_tab_with_none(self):
        with self.assertRaises(TypeError):
            remove_tab_and_text_after_tab(None)

    def test_remove_tab_and_text_after_tab_with_no_tabs(self):
        self.assertEqual("Asd", remove_tab_and_text_after_tab("Asd"))

    def test_remove_tab_and_text_after_tab_with_multiple_tabs(self):
        self.assertEqual(
            "Asd", remove_tab_and_text_after_tab("Asd\tHello\tWorld")
        )

    def test_remove_tab_and_text_after_tab_with_only_tabs(self):
        self.assertEqual("", remove_tab_and_text_after_tab("\t\t"))


class TestRemoveWhitespaceAndTestAfterWhitespace(unittest.TestCase):
    def test_whitespace_and_test_after_whitespace_with_valid_input(self):
        self.assertEqual(
            "Asd", remove_whitespace_and_text_after_whitespace("Asd Hello")
        )

    def test_whitespace_and_test_after_whitespace_with_invalid_input(self):
        with self.assertRaises(TypeError):
            remove_whitespace_and_text_after_whitespace({"key": "value"})

    def test_whitespace_and_test_after_whitespace_with_empty_string(self):
        self.assertEqual("", remove_whitespace_and_text_after_whitespace(""))

    def test_whitespace_and_test_after_whitespace_with_no_whitespaces(self):
        self.assertEqual(
            "Asd", remove_whitespace_and_text_after_whitespace("Asd")
        )

    def test_whitespace_and_test_after_whitespace_with_multiple_whitespaces(
        self,
    ):
        self.assertEqual(
            "Asd", remove_whitespace_and_text_after_whitespace("Asd   Hello")
        )

    def test_whitespace_and_test_after_whitespace_with_only_whitespaces(self):
        self.assertEqual("", remove_whitespace_and_text_after_whitespace("  "))

    def test_whitespace_and_test_after_whitespace_with_no_input(self):
        with self.assertRaises(TypeError):
            remove_whitespace_and_text_after_whitespace()


class TestGetGroupName(unittest.TestCase):
    def test_get_group_name_with_valid_input(self):
        self.assertEqual("", get_group_name("asd"))

    def test_get_group_name_with_invalid_input(self):
        with self.assertRaises(TypeError):
            get_group_name({"key": "value"})

    def test_get_group_name_with_no_input(self):
        with self.assertRaises(TypeError):
            get_group_name()

    def test_get_group_name_with_empty_string(self):
        self.assertEqual("", get_group_name(""))

    def test_get_group_name_with_whitespace(self):
        self.assertEqual("", get_group_name(" "))

    def test_get_group_name_group_pohimeede(self):
        self.assertEqual("Põhimeede", get_group_name("3.2"))

    def test_get_group_name_group_standardmeede(self):
        self.assertEqual("Standardmeede", get_group_name("3.3"))

    def test_get_group_name_group_korgmeede(self):
        self.assertEqual("Kõrgmeede", get_group_name("3.4"))

    def test_get_group_name_group_pohimeede_with_whitespace(self):
        self.assertEqual("", get_group_name(" 3.2 "))


class TestGetRisks(unittest.TestCase):
    def test_get_risks_with_valid_input(self):
        self.assertEqual(get_risks("M1", {"M1": ["R1"]}), ["R1"])

    def test_get_risks_with_invalid_input(self):
        with self.assertRaises(TypeError):
            get_risks({"key": "value"})

    def test_get_risks_with_missing_code(self):
        self.assertEqual(None, get_risks("M2", {"M1": ["R1"]}))

    def test_get_risks_with_empty_code(self):
        self.assertEqual(None, get_risks("", {"M1": ["R1"]}))

    def test_get_risks_with_whitespace_in_code(self):
        self.assertEqual(None, get_risks(" ", {"M1": ["R1"]}))
