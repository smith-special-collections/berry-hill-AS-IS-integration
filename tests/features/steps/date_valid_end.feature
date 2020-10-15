Feature: Date Valid End field

	Scenario: Date Created from Resource
		Given I set the dateValid field to "1917-12-21"
		When I run the export
		Then I should see a <originInfo><dateValid> field with an attribute encoding of "iso8601" and an attribute point of "end" that reads "1917-12-21"