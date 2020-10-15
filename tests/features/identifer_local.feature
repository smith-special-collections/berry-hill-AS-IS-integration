Feature: Local Identifier

  Scenario: Identifier of digital object
    Given I set the digital object component id to "smith_mrbc_ms00001_as38141_00"
    When I run the export
    Then I should see an <identifier> field with attribute type "local" that reads "smith_mrbc_ms00001_as38141_00"
