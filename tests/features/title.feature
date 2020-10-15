Feature: Title Field

  Scenario: Title from the Archival Object
      Given I set the title of the Archival Object to "Hello World"
      And I set the title of the Digital Object to "Not This"
      When I run the export
      Then I should see a <titleInfo><title> tag that reads "Hello World"
      And the <titleInfo><title> tag should not read "Not This"
