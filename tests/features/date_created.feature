Feature: Date Created field

	Scenario: Date Created from Resource
		Given I set the dateCreated field to "1917 Dec 21"
		When I run the export
		Then I should see a <originInfo><dateCreated> field with an attribute keyDate of "yes" that reads "1917 Dec 21"