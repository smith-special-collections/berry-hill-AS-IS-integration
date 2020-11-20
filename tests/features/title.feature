Feature: Title Field

  Scenario: Title from the Digital Object
      Given I set the title of the Digital Object to "Strachey to Woolf"
      And I set the title of the Archival Object to "Not This"
      And I set the date of the Archival Object to "1917 Dec 21"
      Then I should see a <titleInfo><title> tag that reads "Strachey to Woolf,, 1917 Dec 21"
      And I should not see a <titleInfo><title> tag that reads "Not This"
