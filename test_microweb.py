import unittest
import config

from selenium import webdriver

from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


class MicrowebIntegration(unittest.TestCase):

    def setUp(self):
        self.selenium = webdriver.Firefox()
        self.live_server_url = config.SERVER_URL

    def tearDown(self):
        self.selenium.close()

    def test_all(self):
        """
        Run integration tests in a specific sequence, since we do not (yet) have test fixtures.
        """

        self.login()
        self.view_profile()
        self.edit_profile()

        microcosm_id = self.create_microcosm()
        self.edit_microcosm(microcosm_id)

        conversation_id = self.create_conversation(microcosm_id)
        self.edit_conversation(conversation_id)

        self.create_comment_on_item('conversations', conversation_id)

    def login(self):
        """
        Login with Mozilla Persona and assert that the default profile name is correct.
        """

        # Login with persona
        self.selenium.get(self.live_server_url)

        # Click 'login' and switch to persona window
        self.selenium.find_element_by_id('login_link').click()
        self.selenium.switch_to_window('__persona_dialog')

        # Enter email address and password
        # EC.element_to_be_visible was originally used here,
        # but did not seem to wait for the element to be active
        email_address_input = WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="authentication_email"]')))
        email_address_input.send_keys(config.PERSONA_USER)
        self.selenium.find_element_by_xpath('//*[@id="authentication_form"]/p[3]/button[1]').click()

        password_input = WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="authentication_password"]')))
        password_input.send_keys(config.PERSONA_PASS)

        # Submit login form and switch back to previous window
        self.selenium.find_element_by_xpath('//*[@id="authentication_form"]/p[3]/button[2]').click()
        self.selenium.switch_to_window('')

        # Persona login form will be submitted and page reloaded,
        # so wait until profile name is clickable
        profile_name = WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable((By.ID, 'profile_name')))

        # By default profile_name will be set to the
        # local part (before the '@') of the email address
        assert profile_name.text == config.PERSONA_USER.split('@')[0]

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

    def create_comment_on_item(self, item_path, item_id):

        item_url = self.live_server_url + '/' + item_path + '/' + str(item_id)
        self.selenium.get(item_url)

        markdown = 'A test comment with *markdown*\n \
            , line breaks, and [links](http://example.org).'

        comment_box = WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.ID, 'id_markdown')))
        comment_box.send_keys(markdown)
        self.selenium.find_element_by_id('submit_comment').click()

        # Check that we've been redirected to the item page
        # TODO: this will break if there are any URL parameters
        assert item_url == self.selenium.current_url

        #TODO: return the comment ID from the article fragment.

    def edit_comment(self, comment_id):
        self.selenium.get(self.live_server_url + '/comments/' + str(comment_id))

        comment_box = WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.ID, 'id_markdown')))
        comment_box.send_keys(' edited')
        self.selenium.find_element_by_id('submit_comment').click()

if __name__ == "__main__":
    unittest.main()