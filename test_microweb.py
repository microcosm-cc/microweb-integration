import unittest
import config

from selenium import webdriver

from selenium.webdriver.firefox.webdriver import WebDriver
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
        webdriver.find_element_by_id('login_link').click()
        webdriver.switch_to_window('__persona_dialog')

        # Enter email address and password
        email_address_input = WebDriverWait(webdriver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="authentication_email"]')))
        email_address_input.send_keys(config.PERSONA_USER)
        webdriver.find_element_by_xpath('//*[@id="authentication_form"]/p[3]/button[1]').click()

        password_input = WebDriverWait(webdriver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="authentication_password"]')))
        password_input.send_keys(config.PERSONA_PASS)

        # Submit login form and switch back to previous window
        webdriver.find_element_by_xpath('//*[@id="authentication_form"]/p[3]/button[2]').click()
        webdriver.switch_to_window('')

        # Wait until profile name is clickable
        profile_name = WebDriverWait(webdriver, 10).until(
            EC.element_to_be_clickable((By.ID, 'profile_name')))

    @staticmethod
    def logout(server_url, webdriver):

        webdriver.get(server_url)
        WebDriverWait(webdriver, 5).until(
            EC.element_to_be_clickable((By.ID, 'logout'))).click()
        WebDriverWait(webdriver, 5).until(
            EC.element_to_be_clickable((By.ID, 'home'))).click()


class LoginIntegration(unittest.TestCase):

    def setUp(self):
        self.selenium = webdriver.Firefox()
        self.live_server_url = config.SERVER_URL

    def tearDown(self):
        self.selenium.close()

    def test_login(self):
        
        CommonActions.login(self.live_server_url, self.selenium)
        assert self.selenium.find_element_by_id('profile_name').text != ""

    def test_view_profile(self):

        CommonActions.login(self.live_server_url, self.selenium)

        WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.ID, 'profile_name'))).click()

        profile_name = WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable((By.ID, 'profile_name')))

    def test_edit_profile_name(self):

        CommonActions.login(self.live_server_url, self.selenium)

        WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.ID, 'profile_name'))).click()

        WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.ID, 'id_profileName'))).send_keys('_edit')

        WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.ID, 'submit'))).click()

        profile_name = WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.ID, 'profile_name')))
        assert profile_name.text.endswith('_edit')

    def test_logout(self):

        CommonActions.login(self.live_server_url, self.selenium)
        CommonActions.logout(self.live_server_url, self.selenium)

        assert len(self.selenium.find_elements_by_id('login_link')) > 0

    def create_microcosm(self):
        self.selenium.get(self.live_server_url)

        create_microcosm = WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.ID, 'create_microcosm')))
        create_microcosm.click()

        title = WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.ID, 'id_title')))
        title.send_keys('Test microcosm')

        description = WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.ID, 'id_description')))
        description.send_keys('Created by selenium')

        self.selenium.find_element_by_id('submit').click()

        microcosm_title = WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.ID, 'microcosm_title')))
        assert microcosm_title.text == 'Test microcosm'

        microcosm_desc = self.selenium.find_element_by_id('microcosm_description')
        assert microcosm_desc.text == 'Created by selenium'

        return self.selenium.current_url.split('/')[-2]

    def edit_microcosm(self, microcosm_id):
        self.selenium.get(self.live_server_url + '/microcosms/' + str(microcosm_id))
        WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.ID, 'edit_microcosm'))).click()

        title = WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.ID, 'id_title')))
        title.send_keys(' edited')

        edit_reason = WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.ID, 'id_editReason')))
        edit_reason.send_keys('Selenium update')

        WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.ID, 'submit'))).click()

        title = WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.ID, 'microcosm_title')))
        assert 'Test microcosm edited' == title.text

    def view_profile(self):
        self.selenium.get(self.live_server_url)
        WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.ID, 'profile_name'))).click()

        profile_name = WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable((By.ID, 'profile_name')))
        assert profile_name.text == config.PERSONA_USER.split('@')[0]

    def edit_profile(self):
        self.selenium.get(self.live_server_url)
        WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.ID, 'edit_profile'))).click()

        edit_reason = WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.ID, 'id_profileName')))
        edit_reason.send_keys('_edited')

        WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.ID, 'submit'))).click()

        profile_name = WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.ID, 'profile_name')))
        assert profile_name.text == 'personauser_edited'

    def create_conversation(self, microcosm_id):
        # Single microcosm view
        self.selenium.get(self.live_server_url + '/microcosms/' + str(microcosm_id))

        # Click through to item creation page
        WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.ID, 'create_item'))).click()

        # Click to load event creation form
        WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.ID, 'create_conversation'))).click()

        WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.ID, 'id_title'))).send_keys('Conversation test')

        WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.ID, 'submit'))).click()

        title = WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.ID, 'conversation_title')))
        assert title.text == 'Conversation test'

        return self.selenium.current_url.split('/')[-2]

    def edit_conversation(self, conversation_id):
        self.selenium.get(self.live_server_url + '/conversations/' + str(conversation_id))

        old_title = WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.ID, 'conversation_title'))).text

        WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.ID, 'edit_conversation'))).click()

        title = WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.ID, 'id_title')))
        title.send_keys(' edited')

        edit_reason = WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.ID, 'id_editReason')))
        edit_reason.send_keys('Selenium update')

        WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.ID, 'submit'))).click()

        edited_title = WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.ID, 'conversation_title')))

        assert old_title + ' edited' == edited_title.text

    def create_event(self, microcosm_id):
        self.selenium.get(self.live_server_url + '/microcosms/' + str(microcosm_id))

        # Click through to item creation page
        WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.ID, 'create_item'))).click()

        # Click to load event creation form
        WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.ID, 'create_event'))).click()

        title = WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.ID, 'id_title')))
        title.send_keys('Selenium test event')

        where = WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.ID, 'id_where')))
        where.send_keys('London, UK')

        # Click 'locate' to geolocate on the map
        WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.ID, 'locate'))).click()

        WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.ID, 'submit'))).click()

    def create_comment_on_item(self, item_path, item_id):

        item_url = self.live_server_url + '/' + item_path + '/' + str(item_id) + '/'
        self.selenium.get(item_url)

        markdown = 'A test comment with *markdown*\n \
            , line breaks, and [links](http://example.org).'

        comment_box = WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.ID, 'id_markdown')))
        comment_box.send_keys(markdown)
        self.selenium.find_element_by_id('submit_comment').click()

    def edit_comment(self, comment_id):
        self.selenium.get(self.live_server_url + '/comments/' + str(comment_id))

        comment_box = WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.ID, 'id_markdown')))
        comment_box.send_keys(' edited')
        self.selenium.find_element_by_id('submit_comment').click()


if __name__ == "__main__":
    unittest.main()