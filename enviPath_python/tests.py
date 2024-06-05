import unittest
from objects import *
from enviPath import enviPath

class TestAdditionalInformationIntegration(unittest.TestCase):

    def setUp(self):
        # Create an instance of enviPath and log in
        self.eP = enviPath('https://envipath.org')
        self.eP.login('msalz', 'monacl55')

        # Get the package and scenario for setter test
        self.package_id = "https://envipath.org/package/57c34a2f-6310-49b1-92df-a50b5f055d6e"
        self.scen_id = "https://envipath.org/package/57c34a2f-6310-49b1-92df-a50b5f055d6e/scenario/80cc5d47-fa7f-44ce-9522-d0145276b597"
        self.pkg = self.eP.get_package(self.package_id)
        self.scen = self.eP.get_scenario(self.scen_id)

        # Get the package and scenario for parser test
        self.scen_id_parser = "https://envipath.org/package/57c34a2f-6310-49b1-92df-a50b5f055d6e/scenario/f158c00b-0939-4d56-b51b-a0200ce70869"
        self.scen_parser = self.eP.get_scenario(self.scen_id_parser)

    def test_acidity_additional_information(self):

        acidity_info = AcidityAdditionalInformation()
        acidity_info.set_acidityType("water")
        acidity_info.set_highPh(7.0)
        acidity_info.set_lowPh(5.0)

        self.scen.update_scenario(additional_information=[acidity_info_info])

        retrieved_info = self.scen.get_additional_information()[1]



    def test_aeration_type_additional_information(self):
        # Test AerationTypeAdditionalInformation
        aeration_info = AerationTypeAdditionalInformation()
        aeration_info.set_aerationtype("Diffused")

        # Update scenario with the additional information
        self.scen.update_scenario(additional_information=[aeration_info])

        # Retrieve the additional information from the scenario
        retrieved_info = self.scen.get_additional_information()[0]

        # Verify the values for AerationTypeAdditionalInformation
        self.assertEqual(retrieved_info.get_aerationtype(), "Diffused")

    def test_oxygen_uptake_rate_additional_information(self):
        # Test OxygenUptakeRateAdditionalInformation
        oxup = OxygenUptakeRateAdditionalInformation()
        oxup.set_oxygenuptakerateStart(30.0)
        oxup.set_oxygenuptakerateEnd(40.0)

        # Update scenario with the additional information
        self.scen.update_scenario(additional_information=[oxup])

        # Retrieve the additional information from the scenario
        retrieved_info = self.scen.get_additional_information()[2]

        # Verify the values for OxygenUptakeRateAdditionalInformation
        self.assertEqual(retrieved_info.get_oxygenuptakerateStart(), "30.0")
        self.assertEqual(retrieved_info.get_oxygenuptakerateEnd(), "40.0")

    def test_oxygen_demand_additional_information(self):
        # Test OxygenDemandAdditionalInformation
        oxdem = OxygenDemandAdditionalInformation()
        oxdem.set_oxygendemandType("Chemical Oxygen Demand (COD)")
        oxdem.set_oxygendemandInfluent(300.0)
        oxdem.set_oxygendemandEffluent(100.0)

        # Update scenario with the additional information
        self.scen.update_scenario(additional_information=[oxdem])

        # Retrieve the additional information from the scenario
        retrieved_info = self.scen.get_additional_information()[2]

        # Verify the values for OxygenDemandAdditionalInformation
        self.assertEqual(retrieved_info.get_oxygendemandType(), "Chemical Oxygen Demand (COD)")
        self.assertEqual(retrieved_info.get_oxygendemandInfluent(), "300.0")
        self.assertEqual(retrieved_info.get_oxygendemandEffluent(), "100.0")

    def test_dissolved_oxygen_concentration_additional_information(self):
        # Test DissolvedOxygenConcentrationAdditionalInformation
        dissolved_oxygen_data = "2.0;8.0"
        dissolved_oxygen_info = DissolvedOxygenConcentrationAdditionalInformation.parse(dissolved_oxygen_data)

        # Update scenario with the additional information
        self.scen_parser.update_scenario(additional_information=[dissolved_oxygen_info])

        # Retrieve the additional information from the scenario
        retrieved_info = self.scen_parser.get_additional_information()[0]

        # Verify the values for DissolvedOxygenConcentrationAdditionalInformation
        self.assertEqual(retrieved_info.get_DissolvedoxygenconcentrationLow(), "2.0")
        self.assertEqual(retrieved_info.get_DissolvedoxygenconcentrationHigh(), "8.0")

if __name__ == "__main__":
    unittest.main()
