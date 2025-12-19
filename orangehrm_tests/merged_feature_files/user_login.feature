Feature: User Login

  Scenario: User logs in with valid credentials
    Given the user is on the login page
    Given the user has valid credentials
    When the user enters their username
    When the user enters their password
    When the user clicks the login button
    Then the system should authenticate the user
    Then the user should be redirected to the dashboard
    Then the user should see their name displayed on the dashboard

  Scenario: User logs in with invalid credentials
    Given the user is on the login page
    Given the user has invalid credentials
    When the user enters their username
    When the user enters their password
    When the user clicks the login button
    Then the system should fail to authenticate the user
    Then the login page should remain displayed
    Then the user should see ${self.a_link} error message saying 'Invalid credentials'

  Scenario: User attempts to log in with an empty username
    Given the user is on the login page
    Given the username field is empty
    When the user enters their password
    When the user clicks the login button
    Then the system should show a field validation error for the username
    Then the user should remain on the login page

  Scenario: User attempts to log in with an empty password
    Given the user is on the login page
    Given the password field is empty
    When the user enters their username
    When the user clicks the login button
    Then the system should show a field validation error for the password
    Then the user should remain on the login page

  Scenario: User logs in attempting SQL injection
    Given the user is on the login page
    Given the user has an SQL injection string as username
    When the user enters the SQL injection string
    When the user enters a password
    When the user clicks the login button
    Then the system should reject the login attempt
    Then the system should not process the SQL query
    Then the user should see ${self.a_link} error message
