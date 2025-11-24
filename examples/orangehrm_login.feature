Feature: OrangeHRM Login

  As a user
  I want to log in to OrangeHRM
  So that I can access the dashboard

  Scenario: Successful Login
    Given I am on the OrangeHRM login page
    When I enter "username" with value "Admin"
    And I enter "password" with value "admin123"
    And I click on "login_button"
    Then I should see "dashboard"

  Scenario: Invalid Login
    Given I am on the OrangeHRM login page
    When I enter "username" with value "InvalidUser"
    And I enter "password" with value "wrongpassword"
    And I click on "login_button"
    Then I should see "error_message"

