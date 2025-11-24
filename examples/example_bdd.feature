Feature: User Login

  As a user
  I want to log in to the application
  So that I can access my dashboard

  Scenario: Valid Login
    Given I am on the login page
    When I enter "user_name"
    And I enter "password"
    And I click on "submit"
    Then I should see "dashboard"

  Scenario: Invalid Login
    Given I am on the login page
    When I enter "user_name"
    And I enter "password"
    And I click on "submit"
    Then I should see "error_message"

