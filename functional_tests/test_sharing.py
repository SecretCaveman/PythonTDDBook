from selenium import webdriver
from .base import FunctionalTest
from .list_page import ListPage

def quit_if_possible(browser):
	try: browser.quit()
	except: pass


class SharingTest(FunctionalTest):

	def test_can_share_a_list_with_another_user(self):
		#Edith is a logged in user
		self.create_pre_authenticated_session('edith@example.com')
		edith_browser = self.browser
		self.addCleanup(lambda: quit_if_possible(edith_browser))

		#Her friend Oni is also hanging out on the lists site
		oni_browser = webdriver.Firefox()
		self.addCleanup(lambda: quit_if_possible(oni_browser))
		self.browser = oni_browser
		self.create_pre_authenticated_session('oni@example.com')

		#Edith goes to the home page and starts a new list
		self.browser = edith_browser
		self.browser.get(self.live_server_url)
		list_page = ListPage(self).add_list_item('Get help')

		#She notices a "Share this list" option
		share_box = list_page.get_share_box()
		self.assertEqual(
			share_box.get_attribute('placeholder'),
			'your-friend@example.com'
		)

		#She shares her list.
		#The page updates to say that it's shared with Oni
		list_page.share_list_with('oni@example.com')

		#Oni now goes to the lists page with his browser
		self.browser = oni_browser
		MyListsPage(self).go_to_my_lists_page()

		#He sees Edith's list in there
		self.browser.find_element_by_link_text('Get help').click()

		#on the list page, oni can see says that it's Edith's list
		self.wait_for(lambda: self.assertEqual(
			list_page.get_list_owner(),
			'edith@example.com'
		))

		#He adds an item to the list
		list_page.add_list_item('Hi Edith!')

		#When Edith refreshes the page, she sees Onis addition
		self.browser = edith_browser
		self.browser.refresh()
		list_page.wait_for_row_in_list_table('Hi Edith!', 2)
		