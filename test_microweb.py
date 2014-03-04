import unittest
import config
import re

from urlparse import urlparse

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


class CommonActions():
    """
    A set of common actions (e.g. logging in) which are composed within
    individual tests.
    """

    @staticmethod
    def login(server_url, webdriver):

        webdriver.get(server_url)

        # Click login link, switch to persona window
        webdriver.find_element_by_id('login').click()
        webdriver.switch_to_window('__persona_dialog')

        # Enter email address and password
        email_address_input = WebDriverWait(webdriver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="authentication_email"]')))
        email_address_input.send_keys(config.PERSONA_USER)
        webdriver.find_element_by_xpath('//*[@id="authentication_form"]/p[4]/button[1]').click()

        password_input = WebDriverWait(webdriver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="authentication_password"]')))
        password_input.send_keys(config.PERSONA_PASS)

        # Submit login form and switch back to previous window
        webdriver.find_element_by_xpath('//*[@id="authentication_form"]/p[4]/button[3]').click()
        webdriver.switch_to_window('')

        # Wait until profile name is clickable
        WebDriverWait(webdriver, 10).until(
            EC.element_to_be_clickable((By.ID, 'profile')))

    @staticmethod
    def logout(server_url, webdriver):

        webdriver.get(server_url)
        WebDriverWait(webdriver, 10).until(
            EC.element_to_be_clickable((By.ID, 'logout'))).click()

    @staticmethod
    def create_microcosm(server_url, webdriver, title, description):
        """
        Prerequisite: must be viewing a site and have create permission.
        """

        webdriver.get(server_url)

        create_microcosm = WebDriverWait(webdriver, 5).until(
            EC.element_to_be_clickable((By.ID, 'create_microcosm')))
        create_microcosm.click()

        WebDriverWait(webdriver, 5).until(
            EC.element_to_be_clickable((By.ID, 'title'))).send_keys(title)

        WebDriverWait(webdriver, 5).until(
            EC.element_to_be_clickable((By.ID, 'description'))).send_keys(description)

        webdriver.find_element_by_id('submit').click()

        WebDriverWait(webdriver, 5).until(
            EC.element_to_be_clickable((By.ID, 'microcosm_title')))

    @staticmethod
    def create_conversation(webdriver, title, first_post):
        """
        Prerequisite: must be viewing a microcosm and have create permission.
        """

        # Click through to create conversation form
        WebDriverWait(webdriver, 5).until(
            EC.element_to_be_clickable((By.ID, 'create_conversation'))).click()

        WebDriverWait(webdriver, 5).until(
            EC.element_to_be_clickable((By.ID, 'title'))).send_keys(title)

        WebDriverWait(webdriver, 5).until(
            EC.element_to_be_clickable((By.ID, 'reply-box-textarea'))).send_keys(first_post)

        WebDriverWait(webdriver, 5).until(
            EC.element_to_be_clickable((By.ID, 'submit'))).click()

        WebDriverWait(webdriver, 5).until(
            EC.element_to_be_clickable((By.ID, 'title')))

    @staticmethod
    def create_event(webdriver, title, location_string, first_post):
        """
        Prerequisite: must be viewing a microcosm and have create permission.
        """

        # Click to load event creation form
        WebDriverWait(webdriver, 5).until(
            EC.element_to_be_clickable((By.ID, 'create_event'))).click()

        WebDriverWait(webdriver, 5).until(
            EC.element_to_be_clickable((By.ID, 'title'))).send_keys(title)

        WebDriverWait(webdriver, 5).until(
            EC.element_to_be_clickable((By.ID, 'location'))).send_keys(location_string)

        WebDriverWait(webdriver, 5).until(
            EC.element_to_be_clickable((By.ID, 'reply-box-textarea'))).send_keys(first_post)

        # Click 'locate' to geocode the location string and drop map marker
        WebDriverWait(webdriver, 5).until(
            EC.element_to_be_clickable((By.ID, 'locate'))).click()

        # Need to wait until saveLocationState() is finished
        # otherwise form validation will fail
        # TODO: replace this with something that detects when
        # id_lat and id_lon have been populated
        import time; time.sleep(5)

        submit = WebDriverWait(webdriver, 10).until(
            EC.element_to_be_clickable((By.ID, 'submit')))
        submit.click()

    @staticmethod
    def create_comment(webdriver, content):
        """
        Prerequisite: must be viewing an item with a comment box.
        """

        comment_box = WebDriverWait(webdriver, 5).until(
            EC.element_to_be_clickable((By.ID, 'id_markdown')))
        comment_box.send_keys(content)
        webdriver.find_element_by_id('submit_comment').click()

    @staticmethod
    def delete_comment(webdriver, comment_id):

        delete_element_id = 'comment%sdelete' % comment_id
        webdriver.find_element_by_id(delete_element_id).click()
        webdriver.switch_to_alert().accept()
        webdriver.switch_to_window('')

    @staticmethod
    def create_comment_reply(webdriver, content, comment_id):
        """
        Prerequisite: must be viewing an item with the comment with comment_id on the page.
        """
        WebDriverWait(webdriver, 5).until(
            EC.element_to_be_clickable((By.ID, 'comment' + comment_id + 'reply'))).click()
        comment_box = WebDriverWait(webdriver, 5).until(
            EC.element_to_be_clickable((By.ID, 'id_markdown')))
        comment_box.send_keys(content)
        webdriver.find_element_by_id('submit_comment').click()


class LoginIntegration(unittest.TestCase):

    def setUp(self):
        self.selenium = webdriver.Firefox()
        self.live_server_url = config.SERVER_URL

    def tearDown(self):
        self.selenium.close()

    def test_login(self):
        
        CommonActions.login(self.live_server_url, self.selenium)
        assert self.selenium.find_element_by_id('profile').text != ""

    def test_view_profile(self):

        CommonActions.login(self.live_server_url, self.selenium)

        WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.ID, 'profile'))).click()

        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable((By.ID, 'profile')))

    def test_edit_profile(self):

        CommonActions.login(self.live_server_url, self.selenium)

		# Navigate to profile page
        WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.ID, 'edit_profile'))).click()

		# Click "edit profile"
        WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.ID, 'edit_profile_name'))).click()

        WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.ID, 'edit_profile_name'))).clear()

        WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.ID, 'edit_profile_name'))).send_keys('persona_edit')

        WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.ID, 'submit'))).click()

    def test_logout(self):

        CommonActions.login(self.live_server_url, self.selenium)
        CommonActions.logout(self.live_server_url, self.selenium)

        # Login link only visible if logged out
        self.selenium.find_elements_by_id('login_link')


class MicrocosmIntegration(unittest.TestCase):

    def setUp(self):
        self.selenium = webdriver.Firefox()
        self.live_server_url = config.SERVER_URL
        CommonActions.login(self.live_server_url, self.selenium)

    def tearDown(self):
        self.selenium.close()

    def test_create_microcosm(self):

        title = 'Test microcosm'
        description = 'Created by selenium'
        CommonActions.create_microcosm(
            self.live_server_url,
            self.selenium,
            title,
            description
        )

        # Depends on being directed to the newly created microcosm
        microcosm_title = WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.ID, 'microcosm_title')))
        assert microcosm_title.text == title

    def test_edit_microcosm(self):

        title = 'Test microcosm'
        description = 'Created by selenium'
        CommonActions.create_microcosm(
            self.live_server_url,
            self.selenium,
            title,
            description
        )

        WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.ID, 'edit_microcosm'))).click()

        title = WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.ID, 'title')))
        title.send_keys(' edited')

        edit_reason = WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.ID, 'editReason')))
        edit_reason.send_keys('Selenium update')

        WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.ID, 'submit'))).click()

        title = WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.ID, 'microcosm_title')))
        assert title.text.endswith('edited')


class ConversationIntegration(unittest.TestCase):

    def setUp(self):
        self.selenium = webdriver.Firefox()
        self.live_server_url = config.SERVER_URL
        CommonActions.login(self.live_server_url, self.selenium)

    def tearDown(self):
        self.selenium.close()

    def test_create_conversation(self):
        CommonActions.create_microcosm(
            self.live_server_url,
            self.selenium,
            'Microcosm for test conversation',
            'Just a test'
        )

        conversation_title = 'Conversation test'

        CommonActions.create_conversation(
            self.selenium,
            conversation_title,
            'Hi'
        )

        title = WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.ID, 'title')))
        assert title.text == conversation_title

    def test_edit_conversation(self):
        CommonActions.create_microcosm(
            self.live_server_url,
            self.selenium,
            'Microcosm for edited test conversation',
            'Just a test'
        )

        conversation_title = 'Conversation test'

        CommonActions.create_conversation(
            self.selenium,
            conversation_title,
            'Hi'
        )

        WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.ID, 'edit_conversation'))).click()

        title = WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.ID, 'title')))
        title.send_keys(' edited')

        edit_reason = WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.ID, 'editReason')))
        edit_reason.send_keys('Selenium update')

        WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.ID, 'submit'))).click()

        edited_title = WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.ID, 'title')))

        assert edited_title.text.endswith('edited')


class EventIntegration(unittest.TestCase):

    def setUp(self):
        self.selenium = webdriver.Firefox()
        self.live_server_url = config.SERVER_URL
        CommonActions.login(self.live_server_url, self.selenium)

    def tearDown(self):
        self.selenium.close()

    def test_create_event(self):

        CommonActions.create_microcosm(
            self.live_server_url,
            self.selenium,
            'Microcosm for test event',
            'Just a test'
        )

        event_title = 'Test event'

        CommonActions.create_event(
            self.selenium,
            event_title,
            'London, UK',
            'Hi'
        )

        title = WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.ID, 'event_title')))
        assert title.text == event_title

    def test_edit_event(self):

        CommonActions.create_microcosm(
            self.live_server_url,
            self.selenium,
            'Microcosm for edited test event',
            'Just a test'
        )

        CommonActions.create_event(
            self.selenium,
            'Test event',
            'London, UK',
            'First comment'
        )

        WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.ID, 'edit_event'))).click()

        title = WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.ID, 'id_title')))
        title.send_keys(' edited')

        edit_reason = WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.ID, 'id_editReason')))
        edit_reason.send_keys('Selenium update')

        WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.ID, 'submit'))).click()

        edited_title = WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.ID, 'event_title')))

        assert edited_title.text.endswith('edited')


class CommentIntegration(unittest.TestCase):

    content = \
        """A test comment with *markdown*,
        line breaks, [links](http://example.org), another link
        http://example.org, a mention +motter, and a
        <script>small html forbidden fruit</script>.
        """

    def get_created_comment_id(self):
        """
        Parses the ID of the comment that's been created out of the current URL.
        """

        id_match = re.compile('(\D+)(\d+)')
        fragment = urlparse(self.selenium.current_url).fragment
        return id_match.match(fragment).groups()[1]

    def check_hierarchy(self, parents, children):
        for id in parents:
            self.selenium.find_elements_by_id('comment' + str(id))

        for id in children:
            self.selenium.find_elements_by_id('comment' + str(id))


    def setUp(self):
        self.selenium = webdriver.Firefox()
        self.live_server_url = config.SERVER_URL
        CommonActions.login(self.live_server_url, self.selenium)

    def tearDown(self):
        self.selenium.close()

    def get_comment_page(self, comment_id):
        self.selenium.get(config.SERVER_URL + '/comments/' + str(comment_id))

    def test_create_comment_on_event(self):

        CommonActions.create_microcosm(
            self.live_server_url,
            self.selenium,
            'Microcosm for edited test event',
            'Just a test'
        )

        CommonActions.create_event(
            self.selenium,
            'Test event',
            'London, UK'
        )

        CommonActions.create_comment(self.selenium, CommentIntegration.content)

    def test_delete_comment_on_event(self):

        CommonActions.create_microcosm(
            self.live_server_url,
            self.selenium,
            'Microcosm for edited test event',
            'Just a test'
        )

        CommonActions.create_event(
            self.selenium,
            'Test event',
            'London, UK'
        )

        CommonActions.create_comment(self.selenium, CommentIntegration.content)

        comment_id = self.get_created_comment_id()
        CommonActions.delete_comment(self.selenium, comment_id)

    def test_create_comment_on_conversation(self):

        CommonActions.create_microcosm(
            self.live_server_url,
            self.selenium,
            'Microcosm for edited test event',
            'Just a test'
        )

        CommonActions.create_conversation(
            self.selenium,
            'Test conversation',
        )

        CommonActions.create_comment(self.selenium, CommentIntegration.content)

    def test_delete_comment_on_conversation(self):

        CommonActions.create_microcosm(
            self.live_server_url,
            self.selenium,
            'Microcosm for edited test event',
            'Just a test'
        )

        CommonActions.create_conversation(
            self.selenium,
            'Test conversation',
        )

        CommonActions.create_comment(self.selenium, CommentIntegration.content)

        comment_id = self.get_created_comment_id()
        CommonActions.delete_comment(self.selenium, comment_id)

    def test_create_comment_hierarchy(self):

        CommonActions.create_microcosm(
            self.live_server_url,
            self.selenium,
            'Microcosm for testing comment hierarchy',
            'Just a test'
        )

        CommonActions.create_conversation(
            self.selenium,
            'Test conversation',
        )

        CommonActions.create_comment(self.selenium, CommentIntegration.content)
        parent_id = self.get_created_comment_id()

        CommonActions.create_comment_reply(
            self.selenium,
            'Replying to ' + str(parent_id),
            parent_id
        )
        child1_id = self.get_created_comment_id()

        CommonActions.create_comment_reply(
            self.selenium,
            'Another reply to ' + str(parent_id),
            parent_id
        )

        child2_id = self.get_created_comment_id()
        CommonActions.create_comment_reply(
            self.selenium,
            'Replying to ' + str(child2_id),
            child2_id
        )
        gchild_id = self.get_created_comment_id()

        CommonActions.create_comment_reply(
            self.selenium,
            'Replying to ' + str(gchild_id),
            gchild_id
        )
        ggchild1_id = self.get_created_comment_id()

        CommonActions.create_comment_reply(
            self.selenium,
            'Another reply to ' + str(gchild_id),
            gchild_id
        )
        ggchild2_id = self.get_created_comment_id()
        
        CommonActions.create_comment_reply(
            self.selenium,
            'A third reply to ' + str(gchild_id),
            gchild_id
        )
        ggchild3_id = self.get_created_comment_id()
        
        self.get_comment_page(parent_id)
        self.check_hierarchy([],[child1_id, child2_id])

        self.get_comment_page(child1_id)
        self.check_hierarchy([parent_id], [])

        self.get_comment_page(child2_id)
        self.check_hierarchy([parent_id], [gchild_id])

        self.get_comment_page(gchild_id)
        self.check_hierarchy([parent_id, child2_id], [ggchild1_id, ggchild2_id, ggchild3_id])

        self.get_comment_page(ggchild1_id)
        self.check_hierarchy([parent_id, child2_id, gchild_id], [])

class Profiles(unittest.TestCase):

    def setUp(self):
        self.selenium = webdriver.Firefox()
        self.live_server_url = config.SERVER_URL
        CommonActions.login(self.live_server_url, self.selenium)

    def tearDown(self):
        self.selenium.close()

    def test_check_profiles_page_links(self):
        CommonActions.create_microcosm(
            self.live_server_url,
            self.selenium,
            'Microcosm for edited test event',
            'Just a test'
        )

        WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.ID, 'created_by'))).click()

        WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Profiles"))).click()

        WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Sort"))).click()

        WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Sort"))).click()

        WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "u"))).click()

        WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Sort"))).click()

        
if __name__ == "__main__":
    unittest.main()
