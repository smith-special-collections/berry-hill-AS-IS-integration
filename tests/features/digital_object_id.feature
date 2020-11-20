Feature: Digital Object ID

  Scenario: ID from the Digital Object
      Given I set the id of the Digital Object to "smith_mrbc_ms00001_as38141_00"
      Then I should see an <identifier> tag with an attribute of local that reads "smith_mrbc_ms00001_as38141_00"
