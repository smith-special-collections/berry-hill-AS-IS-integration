Feature: Agent Name and Role Field

	Scenario: Agent "Bell, Quentin." and Role from Archival Object
		Given I attach a Person Agent named "Bell, Quentin."" with a role of "creator" to an Archival Object
		When I run the export
		Then I should see a <name> field with an attribute type of "personal" and an attribute authority of "naf"
		And I should see a <name><role><roleTerm> field with an attribute type of "text" and an attribute authority of "marcrelator" that reads "creator"
		And I should see a <name><role><roleTerm> field with an attribute type of "code" and an attribute authority of "marcrelator" that reads "cre"
		And I should see a <name><namePart> field that reads "Bell, Quentin."


	Scenario: Agent "Hogarth Press." and Role from Archival Object
		Given I attach a Person Agent named "Hogarth Press." with a role of "donor" to an Archival Object
		When I run the export
		Then I should see a <name> field with an attribute type of "corporate" and an attribute authority of "lcsh"
		And I should see a <name><role><roleTerm> field with an attribute type of "text" and an attribute authority of "marcrelator" that reads "donor"
		And I should see a <name><role><roleTerm> field with an attribute type of "code" and an attribute authority of "marcrelator" that reads "dnr"
		And I should see a <name><namePart> field that reads "Hogarth Press."
