Feature: Repository Name and Role Field

	Scenario: Repository Name and Role from Repository
		Given I set the repository name to "Mortimer Rare Book Collection (MRBC)"
		When I run the export
		Then I should see a <name><namePart> field that reads "Mortimer Rare Book Collection (MRBC)"
		And I should see a <name><role><roleTerm> field with an attribute authority of "local" and an attribute type of "text" that reads "Unit"

