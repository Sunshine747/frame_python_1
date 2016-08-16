import contextlib
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import stopit
import time


browser = webdriver.Firefox()


@contextlib.contextmanager
def suppress(*exceptions):
	try:
		yield
	except exceptions:
		pass


def wait_for(finder, condition):
	result = None

	with suppress(NoSuchElementException):
		result = finder()

	with stopit.ThreadingTimeout(4) as ctx_mgr:
		while not (result  and condition(result)):
			with suppress(NoSuchElementException):
				time.sleep(0.1)
				result = finder()

	if not ctx_mgr:
		raise stopit.TimeoutException("failed while wating")

	return result


class WaitingElement(object):
	def __init__(self, css_selector):
		self._locator = css_selector
	def _finder(self):
		return browser.find_element_by_css_selector(self._locator)

	def __getattr__(self, item):
		return getattr(self._finder(), item)

	def assure(self, condition):
		wait_for(self._finder, condition)
		return self



def s(css_selector):
	return WaitingElement(css_selector)

browser.get("http://google.com/")
s("[name = 'q']").send_keys("selenium", Keys.ENTER)
s(".srg .g:nth-child(1)").assure(lambda element: "Site of web browser automation tool with .NET provider and related documentation." in element.text)