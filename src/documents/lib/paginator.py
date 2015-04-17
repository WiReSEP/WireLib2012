from django.core.paginator import Paginator


class ShortPaginator(Paginator):
    """ This paginator was intended to to generate next and previous buttons
    for the document_list.html. All private button functions are calculating
    these. The document_list.html expects the buttons representated by the
    PageButton class.
    """
    _left_right_bonus = 4

    def _in_range_button(self, page_no):
        active_page = self.new_page.number

        left_border = active_page - ShortPaginator._left_right_bonus
        right_border = active_page + ShortPaginator._left_right_bonus

        css = ""
        if page_no == active_page:
            css = "active"

        if left_border < page_no < right_border:
            return PageButton(page_no, str(page_no), css)
        return None

    def _skip_to_first_button(self):
        active_page = self.new_page.number
        css = ""
        if active_page < ShortPaginator._left_right_bonus + 1:
            css = "disabled"
        return PageButton(1, "|<-", css)

    def _skip_to_last_button(self, page_no):
        active_page = self.new_page.number
        css = ""
        assert page_no == self.num_pages
        if active_page > self.num_pages - ShortPaginator._left_right_bonus:
            css = "disabled"
        return PageButton(self.num_pages, "->|", css)

    def _left_border_buttons(self):
        btns = []
        active_page = self.new_page.number
        css = ""
        if active_page == 1:
            css = "disabled"
        btns.append(self._skip_to_first_button())
        btns.append(PageButton(active_page - 1, "<<", css))
        return btns

    def _right_border_button(self, page_no):
        last_page = self.num_pages
        if page_no != last_page:
            return
        btns = []
        active_page = self.new_page.number
        css = ""
        if active_page == last_page:
            css = "disabled"
        btns.append(PageButton(active_page + 1, ">>", css))
        btns.append(self._skip_to_last_button(page_no))
        return btns

    def short_page_range(self):
        page_range = self._left_border_buttons()

        for i in self.page_range:
            if self._in_range_button(i):
                page_range.append(self._in_range_button(i))
        else:
            page_range += self._right_border_button(i)

        return page_range

    def page(self, number):
        """ Returns a Page object for the given 1-based page number."""
        self.new_page = super(ShortPaginator, self).page(number)
        return self.new_page


class PageButton:
    def __init__(self, page, label, css_classes):
        self.page = page
        self.label = label
        self.css_classes = css_classes
