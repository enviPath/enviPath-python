import unittest
import inspect
from objects import *
from enviPath import enviPath

class TestAdditionalInformationIntegration(unittest.TestCase):

    def setUp(self):
        # Create an instance of enviPath and log in
        self.eP = enviPath('https://envipath.org')
        self.eP.login('msalz', 'monacl55')

        # Get the package and scenario for setter test
        self.package_id = "https://envipath.org/package/ecf836f9-23de-4642-825c-9fec9e7bce6f"
        self.pkg = self.eP.get_package(self.package_id)

    def get_scenario_name(self):
        # Get the current function name
        current_function_name = inspect.stack()[1].function
        # Extract the second word from the function name
        
        function_words = current_function_name.split('_')
        if 'parser' in function_words:
            scenario_name = function_words[1] + function_words[-1]
        else:
            scenario_name = function_words[1]
        return scenario_name
        

    def test_acidity_additional_information(self):
        scenario_name = self.get_scenario_name()
    

        scen = Scenario.create(self.pkg, name=scenario_name ,description="to test",additional_information= [])

        info = AcidityAdditionalInformation()
        info.set_acidityType("Water")
        info.set_highPh(7.0)
        info.set_lowPh(5.0)

        scen.update_scenario(additional_information=[info])

        retrieved_info = scen.get_additional_information()[0]
        
 
        self.assertEqual(retrieved_info.get_acidityType(), "WATER")
        self.assertEqual(retrieved_info.get_highPh(), 7.0)
        self.assertEqual(retrieved_info.get_lowPh(), 5.0)

    def test_acidity_additional_information_parser(self):
        scenario_name = self.get_scenario_name()

        scen_parser = Scenario.create(self.pkg,name=scenario_name,description="to test",additional_information= [])
        data = "5.0 - 7.0;KCL"
        info = AcidityAdditionalInformation.parse(data)
    
        scen_parser.update_scenario(additional_information=[info])

        retrieved_info = scen_parser.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_acidityType(), "KCL")
        self.assertEqual(retrieved_info.get_highPh(), 7.0)
        self.assertEqual(retrieved_info.get_lowPh(), 5.0)

    
    # acidity ws
    def test_aciditywatersediment_additional_information(self):
        scenario_name = self.get_scenario_name()
        
        scen = Scenario.create(self.pkg, name=scenario_name, description="to test", additional_information=[])

        info = AcidityWaterSedimentAdditionalInformation()
        info.set_pH_water_low(6.0)
        info.set_pH_water_high(8.0)
        info.set_pH_sediment_low(5.5)
        info.set_pH_sediment_high(7.5)
        info.set_acidityType("WATER")

        scen.update_scenario(additional_information=[info])

        retrieved_info = scen.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_pH_water_low(), 6.0)
        self.assertEqual(retrieved_info.get_pH_water_high(), 8.0)
        self.assertEqual(retrieved_info.get_pH_sediment_low(), 5.5)
        self.assertEqual(retrieved_info.get_pH_sediment_high(), 7.5)
        self.assertEqual(retrieved_info.get_acidityType(), "WATER")

    def test_aciditywatersediment_additional_information_parser(self):
        scenario_name = self.get_scenario_name()

        scen_parser = Scenario.create(self.pkg, name=scenario_name, description="to test", additional_information=[])
        data = "6.0 - 8.0;5.5 - 7.5;KCL"
        info = AcidityWaterSedimentAdditionalInformation.parse(data)

        scen_parser.update_scenario(additional_information=[info])

        retrieved_info = scen_parser.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_pH_water_low(), 6.0)
        self.assertEqual(retrieved_info.get_pH_water_high(), 8.0)
        self.assertEqual(retrieved_info.get_pH_sediment_low(), 5.5)
        self.assertEqual(retrieved_info.get_pH_sediment_high(), 7.5)
        self.assertEqual(retrieved_info.get_acidityType(), "KCL")

    # ammonia uptake rate
    def test_ammoniauptakerate_additional_information(self):
        scenario_name = self.get_scenario_name()
        
        scen = Scenario.create(self.pkg, name=scenario_name, description="to test", additional_information=[])

        info = AmmoniaUptakeRateAdditionalInformation()
        info.set_ammoniauptakerateStart(1.0)
        info.set_ammoniauptakerateEnd(5.0)

        scen.update_scenario(additional_information=[info])

        retrieved_info = scen.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_ammoniauptakerateStart(), 1.0)
        self.assertEqual(retrieved_info.get_ammoniauptakerateEnd(), 5.0)


    def test_ammoniauptakerate_additional_information_parser(self):
        scenario_name = self.get_scenario_name()

        scen_parser = Scenario.create(self.pkg, name=scenario_name, description="to test", additional_information=[])
        data = "1.0;5.0"
        info = AmmoniaUptakeRateAdditionalInformation.parse(data)

        scen_parser.update_scenario(additional_information=[info])

        retrieved_info = scen_parser.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_ammoniauptakerateStart(), 1.0)
        self.assertEqual(retrieved_info.get_ammoniauptakerateEnd(), 5.0)

    # biological treatment
    def test_biologicaltreatmenttechnology_additional_information(self):
        scenario_name = self.get_scenario_name()
        allowed_values = ['nitrification', 'nitrification & denitrification', 'nitrification & denitrification & biological phosphorus removal', 'nitrification & denitrification & chemical phosphorus removal', 'other']
        for value in allowed_values:
            scen = Scenario.create(self.pkg, name=scenario_name, description="to test", additional_information=[])

            info = BiologicalTreatmentTechnologyAdditionalInformation()
            info.set_biologicaltreatmenttechnology(value)

            scen.update_scenario(additional_information=[info])

            retrieved_info = scen.get_additional_information()[0]

            self.assertEqual(retrieved_info.get_biologicaltreatmenttechnology(), value)

    def test_biologicaltreatmenttechnology_additional_information_parser(self):
        scenario_name = self.get_scenario_name()
        
        allowed_values = ['nitrification', 'nitrification & denitrification', 'nitrification & denitrification & biological phosphorus removal', 'nitrification & denitrification & chemical phosphorus removal', 'other']
        for value in allowed_values:
            scen_parser = Scenario.create(self.pkg, name=scenario_name, description="to test", additional_information=[])
            data = "Nitrification"
            info = BiologicalTreatmentTechnologyAdditionalInformation.parse(value)

            scen_parser.update_scenario(additional_information=[info])

            retrieved_info = scen_parser.get_additional_information()[0]

            self.assertEqual(retrieved_info.get_biologicaltreatmenttechnology(), value)

    # bioreactor 

    def test_bioreactor_additional_information(self):
        scenario_name = self.get_scenario_name()
        
        scen = Scenario.create(self.pkg, name=scenario_name, description="to test", additional_information=[])

        info = BioreactorAdditionalInformation()
        info.set_bioreactortype("batch")
        info.set_bioreactorsize(500.0)

        scen.update_scenario(additional_information=[info])

        retrieved_info = scen.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_bioreactortype(), "batch")
        self.assertEqual(retrieved_info.get_bioreactorsize(), 500.0)

    def test_bioreactor_additional_information_parser(self):
        scenario_name = self.get_scenario_name()

        scen_parser = Scenario.create(self.pkg, name=scenario_name, description="to test", additional_information=[])
        data = "batch;500.0"
        info = BioreactorAdditionalInformation.parse(data)

        scen_parser.update_scenario(additional_information=[info])

        retrieved_info = scen_parser.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_bioreactortype(), "batch")
        self.assertEqual(retrieved_info.get_bioreactorsize(), 500.0)

    def test_bioreactor_additional_information_parser_comma(self):
        scenario_name = self.get_scenario_name()

        scen_parser = Scenario.create(self.pkg, name=scenario_name, description="to test", additional_information=[])
        data = "batch, 500.0"
        info = BioreactorAdditionalInformation.parse(data)

        scen_parser.update_scenario(additional_information=[info])

        retrieved_info = scen_parser.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_bioreactortype(), "batch")
        self.assertEqual(retrieved_info.get_bioreactorsize(), 500.0)



    # biomass
    def test_biomass_additional_information(self):
        scenario_name = self.get_scenario_name()
        
        scen = Scenario.create(self.pkg, name=scenario_name, description="to test", additional_information=[])

        info = BioMassAdditionalInformation()
        info.set_biomassStart(1.0)
        info.set_biomassEnd(5.0)

        scen.update_scenario(additional_information=[info])

        retrieved_info = scen.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_biomassStart(), 1.0)
        self.assertEqual(retrieved_info.get_biomassEnd(), 5.0)

    def test_biomass_additional_information_parser(self):
        scenario_name = self.get_scenario_name()

        scen_parser = Scenario.create(self.pkg, name=scenario_name, description="to test", additional_information=[])
        data = "1.0 - 5.0"
        info = BioMassAdditionalInformation.parse(data)

        scen_parser.update_scenario(additional_information=[info])

        retrieved_info = scen_parser.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_biomassStart(), 1.0)
        self.assertEqual(retrieved_info.get_biomassEnd(), 5.0)

    # biomass ws
    def test_biomasswatersediment_additional_information(self):
        scenario_name = self.get_scenario_name()
        
        scen = Scenario.create(self.pkg, name=scenario_name, description="to test", additional_information=[])

        info = BioMassWaterSedimentAdditionalInformation()
        info.set_start_water_cells(100.0)
        info.set_end_water_cells(200.0)
        info.set_start_sediment_cells(300.0)
        info.set_end_sediment_cells(400.0)
        info.set_start_sediment_mg(0.5)
        info.set_end_sediment_mg(1.0)

        scen.update_scenario(additional_information=[info])

        retrieved_info = scen.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_start_water_cells(), 100.0)
        self.assertEqual(retrieved_info.get_end_water_cells(), 200.0)
        self.assertEqual(retrieved_info.get_start_sediment_cells(), 300.0)
        self.assertEqual(retrieved_info.get_end_sediment_cells(), 400.0)
        self.assertEqual(retrieved_info.get_start_sediment_mg(), 0.5)
        self.assertEqual(retrieved_info.get_end_sediment_mg(), 1.0)

    def test_biomasswatersediment_additional_information_parser(self):
        scenario_name = self.get_scenario_name()

        scen_parser = Scenario.create(self.pkg, name=scenario_name, description="to test", additional_information=[])
        data = "100 - 200;300 - 400;0.5 - 1.0"
        info = BioMassWaterSedimentAdditionalInformation.parse(data)

        scen_parser.update_scenario(additional_information=[info])

        retrieved_info = scen_parser.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_start_water_cells(), 100.0)
        self.assertEqual(retrieved_info.get_end_water_cells(), 200.0)
        self.assertEqual(retrieved_info.get_start_sediment_cells(), 300.0)
        self.assertEqual(retrieved_info.get_end_sediment_cells(), 400.0)
        self.assertEqual(retrieved_info.get_start_sediment_mg(), 0.5)
        self.assertEqual(retrieved_info.get_end_sediment_mg(), 1.0)

    # bulk density 
    def test_bulkdensity_additional_information(self):
        scenario_name = self.get_scenario_name()
        
        scen = Scenario.create(self.pkg, name=scenario_name, description="to test", additional_information=[])

        info = BulkDensityAdditionalInformation()
        info.set_bulkdensity(1.5)

        scen.update_scenario(additional_information=[info])

        retrieved_info = scen.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_bulkdensity(), 1.5)

    def test_bulkdensity_additional_information_parser(self):
        scenario_name = self.get_scenario_name()

        scen_parser = Scenario.create(self.pkg, name=scenario_name, description="to test", additional_information=[])
        data = "1.5"
        info = BulkDensityAdditionalInformation.parse(data)

        scen_parser.update_scenario(additional_information=[info])

        retrieved_info = scen_parser.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_bulkdensity(), 1.5)

    # cec

    def test_cec_additional_information(self):
        scenario_name = self.get_scenario_name()
        
        scen = Scenario.create(self.pkg, name=scenario_name, description="to test", additional_information=[])

        info = CECAdditionalInformation()
        info.set_cecdata(10.5)

        scen.update_scenario(additional_information=[info])

        retrieved_info = scen.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_cecdata(), 10.5)

    def test_cec_additional_information_parser(self):
        scenario_name = self.get_scenario_name()

        scen_parser = Scenario.create(self.pkg, name=scenario_name, description="to test", additional_information=[])
        data = "10.5"
        info = CECAdditionalInformation.parse(data)

        scen_parser.update_scenario(additional_information=[info])

        retrieved_info = scen_parser.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_cecdata(), 10.5)
        
    # confidence level
    def test_confidencelevel_information(self):
        test_data = [
            "1",
            "2",
            "3"
        ]

        for level in test_data:
            info = ConfidenceLevelAdditionalInformation()

            
            scen = Scenario.create(self.pkg, name=self.get_scenario_name(), description="to test Confidence Level",
                                   additional_information=[])

            info.set_radioconfidence(level)

            
            scen.update_scenario(additional_information=[info])
            retrieved_info = scen.get_additional_information()[0]

            self.assertEqual(retrieved_info.get_radioconfidence(), level)

    def test_confidencelevel_parser(self):
        data_string = "1"
        info = ConfidenceLevelAdditionalInformation.parse(data_string)

        
        scen = Scenario.create(self.pkg, name=self.get_scenario_name(), description="to test Confidence Level parser",
                               additional_information=[])

        
        scen.update_scenario(additional_information=[info])
        retrieved_info = scen.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_radioconfidence(), "1")

    def test_invalid_confidence_level(self):
        with self.assertRaises(ValueError):
            ConfidenceLevelAdditionalInformation().set_radioconfidence("Invalid")
    # columnheight

    def test_columnheight_additional_information(self):
        scenario_name = self.get_scenario_name()
        
        scen = Scenario.create(self.pkg, name=scenario_name, description="to test column height", additional_information=[])

        info = ColumnHeightAdditionalInformation()
        info.set_column_height_water(15.0)
        info.set_column_height_sediment(10.0)

        scen.update_scenario(additional_information=[info])

        retrieved_info = scen.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_column_height_water(), 15.0)
        self.assertEqual(retrieved_info.get_column_height_sediment(), 10.0)

    def test_columnheight_additional_information_parser(self):
        scenario_name = self.get_scenario_name()

        scen_parser = Scenario.create(self.pkg, name=scenario_name, description="to test column height parser", additional_information=[])
        data = "10.0;15.0"
        info = ColumnHeightAdditionalInformation.parse(data)

        scen_parser.update_scenario(additional_information=[info])

        retrieved_info = scen_parser.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_column_height_water(), 15.0)
        self.assertEqual(retrieved_info.get_column_height_sediment(), 10.0)

    # dissolved organic carbon

    def test_dissolvedorganiccarbon_additional_information(self):
        scenario_name = self.get_scenario_name()
        
        scen = Scenario.create(self.pkg, name=scenario_name, description="to test dissolved organic carbon", additional_information=[])

        info = DissolvedOrganicCarbonAdditionalInformation()
        info.set_dissolvedorganiccarbonStart(5.2)
        info.set_dissolvedorganiccarbonEnd(10.5)

        scen.update_scenario(additional_information=[info])

        retrieved_info = scen.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_dissolvedorganiccarbonStart(), 5.2)
        self.assertEqual(retrieved_info.get_dissolvedorganiccarbonEnd(), 10.5)

    def test_dissolvedorganiccarbon_additional_information_parser(self):
        scenario_name = self.get_scenario_name()

        scen_parser = Scenario.create(self.pkg, name=scenario_name, description="to test dissolved organic carbon parser", additional_information=[])
        data = "5.2;10.5"
        info = DissolvedOrganicCarbonAdditionalInformation.parse(data)

        scen_parser.update_scenario(additional_information=[info])

        retrieved_info = scen_parser.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_dissolvedorganiccarbonStart(), 5.2)
        self.assertEqual(retrieved_info.get_dissolvedorganiccarbonEnd(), 10.5)

    # final compound concentration
    def test_finalcompoundconcentration_additional_information(self):
        scenario_name = self.get_scenario_name()
        
        scen = Scenario.create(self.pkg, name=scenario_name, description="to test final compound concentration", additional_information=[])

        info = FinalCompoundConcentrationAdditionalInformation()
        info.set_finalcompoundconcentration(25.4)

        scen.update_scenario(additional_information=[info])

        retrieved_info = scen.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_finalcompoundconcentration(), 25.4)

    def test_finalcompoundconcentration_additional_information_parser(self):
        scenario_name = self.get_scenario_name()

        scen_parser = Scenario.create(self.pkg, name=scenario_name, description="to test final compound concentration parser", additional_information=[])
        data = "25.4"
        info = FinalCompoundConcentrationAdditionalInformation.parse(data)

        scen_parser.update_scenario(additional_information=[info])

        retrieved_info = scen_parser.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_finalcompoundconcentration(), 25.4)

# half-life ws
    def test_halflifews_additional_information_parser(self):
        scenario_name = self.get_scenario_name()

        scen_parser = Scenario.create(self.pkg, name=scenario_name, description="to test half-life water sediment parser", additional_information=[])
        data = "Test model ws;Test fit ws;Test comment ws;5.0 - 10.0;1.0 - 2.0;3.0 - 4.0;reported"
        info = HalfLifeWaterSedimentAdditionalInformation.parse(data)

        scen_parser.update_scenario(additional_information=[info])

        retrieved_info = scen_parser.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_total_low(), 5.0)
        self.assertEqual(retrieved_info.get_total_high(), 10.0)
        self.assertEqual(retrieved_info.get_water_low(), 1.0)
        self.assertEqual(retrieved_info.get_water_high(), 2.0)
        self.assertEqual(retrieved_info.get_sediment_low(), 3.0)
        self.assertEqual(retrieved_info.get_sediment_high(), 4.0)
        self.assertEqual(retrieved_info.get_fit_ws(), "Test fit ws")
        self.assertEqual(retrieved_info.get_model_ws(), "Test model ws")
        self.assertEqual(retrieved_info.get_comment_ws(), "Test comment ws")
        self.assertEqual(retrieved_info.get_source_ws(), "reported")
    # half life
    """ def test_halflife_additional_information(self):
        scenario_name = self.get_scenario_name()
        
        scen = Scenario.create(self.pkg, name=scenario_name, description="to test half-life", additional_information=[])

        info = HalfLifeAdditionalInformation()
        info.set_lower(5.0)
        info.set_upper(10.0)
        info.set_comment("Test comment")
        info.set_source("reported")
        info.set_firstOrder(True)
        #info.set_model("Test model")
        info.set_fit("Test fit")

        scen.update_scenario(additional_information=[info])

        retrieved_info = scen.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_lower(), 5.0)
        self.assertEqual(retrieved_info.get_upper(), 10.0)
        self.assertEqual(retrieved_info.get_comment(), "Test comment")
        self.assertEqual(retrieved_info.get_source(), "reported")
        self.assertTrue(retrieved_info.get_firstOrder(),None)
        self.assertEqual(retrieved_info.get_model(), "Test model")
        self.assertEqual(retrieved_info.get_fit(), "Test fit")

    def test_halflife_additional_information_parser(self):
        scenario_name = self.get_scenario_name()

        scen_parser = Scenario.create(self.pkg, name=scenario_name, description="to test half-life parser", additional_information=[])
        data = "SFO;Test fit;Test comment;5.0 - 10.0;reported"
        info = HalfLifeAdditionalInformation.parse(data)

        scen_parser.update_scenario(additional_information=[info])

        retrieved_info = scen_parser.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_lower(), 5.0)
        self.assertEqual(retrieved_info.get_upper(), 10.0)
        self.assertEqual(retrieved_info.get_comment(), "Test comment")
        self.assertEqual(retrieved_info.get_source(), "reported")
        self.assertIsNone(retrieved_info.get_firstOrder(),True)  # Assuming not set in the parser
        self.assertEqual(retrieved_info.get_model(), "SFO")
        self.assertEqual(retrieved_info.get_fit(), "Test fit")
 """ 
    # humidity 
    def test_humidity_additional_information(self):
        scenario_name = self.get_scenario_name()
        
        scen = Scenario.create(self.pkg, name=scenario_name, description="to test humidity", additional_information=[])

        info = HumidityAdditionalInformation()
        info.set_expHumid(55.0)

        scen.update_scenario(additional_information=[info])

        retrieved_info = scen.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_expHumid(), 55.0)

    def test_humidity_additional_information_parser(self):
        scenario_name = self.get_scenario_name()

        scen_parser = Scenario.create(self.pkg, name=scenario_name, description="to test humidity parser", additional_information=[])
        data = "55.0"
        info = HumidityAdditionalInformation.parse(data)

        scen_parser.update_scenario(additional_information=[info])

        retrieved_info = scen_parser.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_expHumid(), 55.0)

    def test_humidity_additional_information_invalid_value(self):
        info = HumidityAdditionalInformation()
        
        with self.assertRaises(ValueError):
            info.set_expHumid(110.0)  # Invalid value, should raise ValueError
        
        with self.assertRaises(ValueError):
            info.set_expHumid(-10.0)  # Invalid value, should raise ValueError

        with self.assertRaises(ValueError):
            info.set_expHumid("high")  # Invalid type, should raise ValueError

    # initial mass sediment

    def test_initialmass_sediment_additional_information(self):
        scenario_name = self.get_scenario_name()
        
        scen = Scenario.create(self.pkg, name=scenario_name, description="to test initial mass sediment", additional_information=[])

        info = InitialMassSedimentAdditionalInformation()
        info.set_initial_mass_sediment(120.0)
        info.set_wet_or_dry('WET')

        scen.update_scenario(additional_information=[info])

        retrieved_info = scen.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_initial_mass_sediment(), 120.0)
        self.assertEqual(retrieved_info.get_wet_or_dry(), 'WET')

    def test_initialmasssediment_additional_information_parser(self):
        scenario_name = self.get_scenario_name()

        scen_parser = Scenario.create(self.pkg, name=scenario_name, description="to test initial mass sediment parser", additional_information=[])
        data = "120.0;WET"
        info = InitialMassSedimentAdditionalInformation.parse(data)

        scen_parser.update_scenario(additional_information=[info])

        retrieved_info = scen_parser.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_initial_mass_sediment(), 120.0)
        self.assertEqual(retrieved_info.get_wet_or_dry(), 'WET')

    def test_initialmasssediment_additional_information_invalid_value(self):
        info = InitialMassSedimentAdditionalInformation()
        
        with self.assertRaises(ValueError):
            info.set_initial_mass_sediment("heavy")  # Invalid type, should raise ValueError
        
        with self.assertRaises(ValueError):
            info.set_wet_or_dry("damp")  # Invalid value, should raise ValueError

    # initial volume water
    def test_initialvolumewater_additional_information(self):
        scenario_name = self.get_scenario_name()
        
        scen = Scenario.create(self.pkg, name=scenario_name, description="to test initial volume water", additional_information=[])

        info = InitialVolumeWaterAdditionalInformation()
        info.set_initialvolumewater(500.0)

        scen.update_scenario(additional_information=[info])

        retrieved_info = scen.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_initialvolumewater(), 500.0)

    def test_initialvolumewater_additional_information_parser(self):
        scenario_name = self.get_scenario_name()

        scen_parser = Scenario.create(self.pkg, name=scenario_name, description="to test initial volume water parser", additional_information=[])
        data = "500.0"
        info = InitialVolumeWaterAdditionalInformation.parse(data)

        scen_parser.update_scenario(additional_information=[info])

        retrieved_info = scen_parser.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_initialvolumewater(), 500.0)

    def test_initialvolumewater_additional_information_invalid_value(self):
        info = InitialVolumeWaterAdditionalInformation()
        
        with self.assertRaises(ValueError):
            info.set_initialvolumewater("five hundred")  # Invalid type, should raise ValueError


    # inoculum source
    
    def test_inoculumsource_additional_information(self):
        scenario_name = self.get_scenario_name()
        
        scen = Scenario.create(self.pkg, name=scenario_name, description="to test inoculum source", additional_information=[])

        info = InoculumSourceAdditionalInformation()
        info.set_inoculumsource("river sediment")

        scen.update_scenario(additional_information=[info])

        retrieved_info = scen.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_inoculumsource(), "river sediment")

    def test_inoculumsource_additional_information_parser(self):
        scenario_name = self.get_scenario_name()

        scen_parser = Scenario.create(self.pkg, name=scenario_name, description="to test inoculum source parser", additional_information=[])
        data = "river sediment"
        info = InoculumSourceAdditionalInformation.parse(data)

        scen_parser.update_scenario(additional_information=[info])

        retrieved_info = scen_parser.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_inoculumsource(), "river sediment")


    def test_lag_phase_additional_information(self):
        scenario_name = self.get_scenario_name()
        
        scen = Scenario.create(self.pkg, name=scenario_name, description="to test lag phase", additional_information=[])

        info = LagPhaseAdditionalInformation()
        info.set_lagphase(5.0)

        scen.update_scenario(additional_information=[info])

        retrieved_info = scen.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_lagphase(), 5.0)

    def test_lag_phase_additional_information_parser(self):
        scenario_name = self.get_scenario_name()

        scen_parser = Scenario.create(self.pkg, name=scenario_name, description="to test lag phase parser", additional_information=[])
        data = "6.0"
        info = LagPhaseAdditionalInformation.parse(data)

        scen_parser.update_scenario(additional_information=[info])

        retrieved_info = scen_parser.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_lagphase(), 6.0)
    # location 
    def test_location_additional_information(self):
        scenario_name = self.get_scenario_name()
        
        scen = Scenario.create(self.pkg, name=scenario_name, description="to test location", additional_information=[])

        info = LocationAdditionalInformation()
        info.set_location("Sample location")

        scen.update_scenario(additional_information=[info])

        retrieved_info = scen.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_location(), "Sample location")

    def test_location_additional_information_parser(self):
        scenario_name = self.get_scenario_name()

        scen_parser = Scenario.create(self.pkg, name=scenario_name, description="to test location parser", additional_information=[])
        data = "Sample location"
        info = LocationAdditionalInformation.parse(data)

        scen_parser.update_scenario(additional_information=[info])

        retrieved_info = scen_parser.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_location(), "Sample location")
    # sample location 
    def test_samplelocation_additional_information(self):
        scenario_name = self.get_scenario_name()
        
        scen = Scenario.create(self.pkg, name=scenario_name, description="to test sample location", additional_information=[])

        info = SampleLocationAdditionalInformation()
        info.set_samplelocation("Sample location for water-sediment study")

        scen.update_scenario(additional_information=[info])

        retrieved_info = scen.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_samplelocation(), "Sample location for water-sediment study")

    def test_samplelocation_additional_information_parser(self):
        scenario_name = self.get_scenario_name()

        scen_parser = Scenario.create(self.pkg, name=scenario_name, description="to test sample location parser", additional_information=[])
        data = "Sample location for water-sediment study"
        info = SampleLocationAdditionalInformation.parse(data)

        scen_parser.update_scenario(additional_information=[info])

        retrieved_info = scen_parser.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_samplelocation(), "Sample location for water-sediment study")


    # solvent for compound solution

    def test_solventforcompoundsolution_valid_solvents(self):
        scenario_name = self.get_scenario_name()
        valid_solvents = ["MeOH", "EtOH", "H2O", "DMSO", "acetone"]
        
        for solvent in valid_solvents:
            with self.subTest(solvent=solvent):
                scen = Scenario.create(self.pkg, name=scenario_name, description="to test", additional_information=[])
                
                solvent_info = SolventForCompoundSolutionAdditionalInformation()
                solvent_info.set_solventforcompoundsolution1(solvent)
                solvent_info.set_solventforcompoundsolution2("H2O")
                solvent_info.set_solventforcompoundsolution3("acetone")
                solvent_info.set_proportion("1:2:1")

                scen.update_scenario(additional_information=[solvent_info])

                retrieved_info = scen.get_additional_information()[0]

                self.assertEqual(retrieved_info.get_solventforcompoundsolution1(), solvent)
                self.assertEqual(retrieved_info.get_solventforcompoundsolution2(), "H2O")
                self.assertEqual(retrieved_info.get_solventforcompoundsolution3(), "acetone")
                self.assertEqual(retrieved_info.get_proportion(), "1:2:1")

    def test_solventforcompoundsolution_parser_valid_solvents(self):
        scenario_name = self.get_scenario_name()
        valid_solvents = ["MeOH", "EtOH", "H2O", "DMSO", "acetone"]
        
        for solvent in valid_solvents:
            with self.subTest(solvent=solvent):
                scen_parser = Scenario.create(self.pkg, name=scenario_name, description="to test", additional_information=[])
                data = f"{solvent};H2O;acetone;1:2:1"
                info = SolventForCompoundSolutionAdditionalInformation.parse(data)

                scen_parser.update_scenario(additional_information=[info])

                retrieved_info = scen_parser.get_additional_information()[0]

                self.assertEqual(retrieved_info.get_solventforcompoundsolution1(), solvent)
                self.assertEqual(retrieved_info.get_solventforcompoundsolution2(), "H2O")
                self.assertEqual(retrieved_info.get_solventforcompoundsolution3(), "acetone")
                self.assertEqual(retrieved_info.get_proportion(), "1:2:1")



    # nitogen content
    def test_nitrogen_content_additional_information(self):
        scenario_name = self.get_scenario_name()

        scen = Scenario.create(self.pkg, name=scenario_name, description="to test nitrogen content", additional_information=[])

        info = NitrogenContentAdditionalInformation()
        info.set_nitrogencontentType("NH4MINUSN")
        info.set_nitrogencontentInfluent(5.0)
        info.set_nitrogencontentEffluent(3.0)

        scen.update_scenario(additional_information=[info])

        retrieved_info = scen.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_nitrogencontentType(), "NH&#8324-N")
        self.assertEqual(retrieved_info.get_nitrogencontentInfluent(), 5.0)
        self.assertEqual(retrieved_info.get_nitrogencontentEffluent(), 3.0)

    def test_nitrogen_content_additional_information_parser(self):
        scenario_name = self.get_scenario_name()

        scen_parser = Scenario.create(self.pkg, name=scenario_name, description="to test nitrogen content parser", additional_information=[])
        data = "NTOT;5.0;3.0"
        info = NitrogenContentAdditionalInformation.parse(data)

        scen_parser.update_scenario(additional_information=[info])

        retrieved_info = scen_parser.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_nitrogencontentType(), "N&#8348&#8338&#8348")
        self.assertEqual(retrieved_info.get_nitrogencontentInfluent(), 5.0)
        self.assertEqual(retrieved_info.get_nitrogencontentEffluent(), 3.0)


    # nutrients addition

    def test_nutrients_additional_information(self):
        scenario_name = self.get_scenario_name()

        scen = Scenario.create(self.pkg, name=scenario_name, description="to test nutrients additional information", additional_information=[])

        info = NutrientsAdditionalInformation()
        nutrients_info = "Adding nutrients to enhance growth"
        info.set_additionofnutrients(nutrients_info)

        scen.update_scenario(additional_information=[info])

        retrieved_info = scen.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_additionofnutrients(), nutrients_info)

    def test_nutrients_additional_information_parser(self):
        scenario_name = self.get_scenario_name()

        scen_parser = Scenario.create(self.pkg, name=scenario_name, description="to test nutrients additional information parser", additional_information=[])
        data = "Adding nutrients to enhance growth"
        info = NutrientsAdditionalInformation.parse(data)

        scen_parser.update_scenario(additional_information=[info])

        retrieved_info = scen_parser.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_additionofnutrients(), data)
        

    # OM content
    def test_omcontentinOM_additional_information(self):
        scenario_name = self.get_scenario_name()

        scen = Scenario.create(self.pkg, name=scenario_name, description="to test OM content additional information in OM", additional_information=[])

        info = OMContentAdditionalInformation()
        om_content = 50.0
        info.set_omcontentInOM(om_content)

        scen.update_scenario(additional_information=[info])

        retrieved_info = scen.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_omcontentInOM(), om_content)

    def test_omcontentinOC_additional_information(self):
        scenario_name = self.get_scenario_name()

        scen = Scenario.create(self.pkg, name=scenario_name, description="to test OM content additional information in OC", additional_information=[])

        info = OMContentAdditionalInformation()
        oc_content = 20.0
        info.set_omcontentINOC(oc_content)

        scen.update_scenario(additional_information=[info])

        retrieved_info = scen.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_omcontentINOC(), oc_content)

    def test_omcontentinOM_additional_information_parser(self):
        scenario_name = self.get_scenario_name()

        scen_parser = Scenario.create(self.pkg, name=scenario_name, description="to test OM content additional information parser", additional_information=[])
        data = "50.0;OM"
        info = OMContentAdditionalInformation.parse(data)

        scen_parser.update_scenario(additional_information=[info])

        retrieved_info = scen_parser.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_omcontentInOM(), 50.0)
        self.assertIsNone(retrieved_info.get_omcontentINOC())

    def test_omcontentinOC_additional_information_parser(self):
        scenario_name = self.get_scenario_name()

        scen_parser = Scenario.create(self.pkg, name=scenario_name, description="to test OM content additional information parser with OC", additional_information=[])
        data = "20.0;OC"
        info = OMContentAdditionalInformation.parse(data)

        scen_parser.update_scenario(additional_information=[info])

        retrieved_info = scen_parser.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_omcontentINOC(), 20.0)
        self.assertIsNone(retrieved_info.get_omcontentInOM())

    # Organiccarbonwater

    def test_organiccarbonwatersetters_additional_information(self):
        scenario_name = self.get_scenario_name()

        scen = Scenario.create(self.pkg, name=scenario_name, description="to test organic carbon water additional information setters", additional_information=[])

        info = OrganicCarbonWaterAdditionalInformation()
        toc_low = 1.5
        toc_high = 3.0
        doc_low = 0.5
        doc_high = 1.5

        info.set_TOC_low(toc_low)
        info.set_TOC_high(toc_high)
        info.set_DOC_low(doc_low)
        info.set_DOC_high(doc_high)

        scen.update_scenario(additional_information=[info])

        retrieved_info = scen.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_TOC_low(), toc_low)
        self.assertEqual(retrieved_info.get_TOC_high(), toc_high)
        self.assertEqual(retrieved_info.get_DOC_low(), doc_low)
        self.assertEqual(retrieved_info.get_DOC_high(), doc_high)

    def test_organiccarbonwaterpartial_toc_additional_information_setters(self):
        scenario_name = self.get_scenario_name()

        scen = Scenario.create(self.pkg, name=scenario_name, description="to test partial TOC settings", additional_information=[])

        info = OrganicCarbonWaterAdditionalInformation()
        toc_low = 1.5

        info.set_TOC_low(toc_low)

        scen.update_scenario(additional_information=[info])

        retrieved_info = scen.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_TOC_low(), toc_low)
        self.assertEqual(retrieved_info.get_TOC_high(),toc_low)
        self.assertIsNone(retrieved_info.get_DOC_low())
        self.assertIsNone(retrieved_info.get_DOC_high())

    def test_organiccarbonwaterpartial_doc_additional_information_setters(self):
        scenario_name = self.get_scenario_name()

        scen = Scenario.create(self.pkg, name=scenario_name, description="to test partial DOC settings", additional_information=[])

        info = OrganicCarbonWaterAdditionalInformation()
        doc_high = 1.5

        info.set_DOC_high(doc_high)

        scen.update_scenario(additional_information=[info])

        retrieved_info = scen.get_additional_information()[0]

        self.assertIsNone(retrieved_info.get_TOC_low())
        self.assertIsNone(retrieved_info.get_TOC_high())
        self.assertEqual(retrieved_info.get_DOC_low(),doc_high)
        self.assertEqual(retrieved_info.get_DOC_high(), doc_high)

    def test_organiccarbonwater_additional_information_parser(self):
        scenario_name = self.get_scenario_name()

        scen_parser = Scenario.create(self.pkg, name=scenario_name, description="to test organic carbon water additional information parser", additional_information=[])
        data = "1.5 - 3.0;0.5 - 1.5"
        info = OrganicCarbonWaterAdditionalInformation.parse(data)

        scen_parser.update_scenario(additional_information=[info])

        retrieved_info = scen_parser.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_TOC_low(), 1.5)
        self.assertEqual(retrieved_info.get_TOC_high(), 3.0)
        self.assertEqual(retrieved_info.get_DOC_low(), 0.5)
        self.assertEqual(retrieved_info.get_DOC_high(), 1.5)

    def test_organiccarbonwaterwith_na_additional_information_parser(self):
        scenario_name = self.get_scenario_name()

        scen_parser = Scenario.create(self.pkg, name=scenario_name, description="to test organic carbon water additional information parser with NA values", additional_information=[])
        data = "NA;0.5 - 1.5"
        info = OrganicCarbonWaterAdditionalInformation.parse(data)

        scen_parser.update_scenario(additional_information=[info])

        retrieved_info = scen_parser.get_additional_information()[0]

        self.assertIsNone(retrieved_info.get_TOC_low())
        self.assertIsNone(retrieved_info.get_TOC_high())
        self.assertEqual(retrieved_info.get_DOC_low(), 0.5)
        self.assertEqual(retrieved_info.get_DOC_high(), 1.5)

    def test_organiccarbonwaterpartial_mixed_additional_information_setters(self):
        scenario_name = self.get_scenario_name()

        scen = Scenario.create(self.pkg, name=scenario_name, description="to test partial mixed TOC and DOC settings", additional_information=[])

        info = OrganicCarbonWaterAdditionalInformation()
        toc_high = 3.0
        doc_low = 0.5

        info.set_TOC_high(toc_high)
        info.set_DOC_low(doc_low)

        scen.update_scenario(additional_information=[info])

        retrieved_info = scen.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_TOC_low(),toc_high)
        self.assertEqual(retrieved_info.get_TOC_high(), toc_high)
        self.assertEqual(retrieved_info.get_DOC_low(), doc_low)
        self.assertEqual(retrieved_info.get_DOC_high(),doc_low)


    # organic content


    def test_organiccontentsetters_additional_information(self):
        scenario_name = self.get_scenario_name()

        scen = Scenario.create(self.pkg, name=scenario_name, description="to test organic content additional information setters", additional_information=[])

        info = OrganicContentAdditionalInformation()
        oc_low = 1.5
        oc_high = 3.0
        om_low = 0.5
        om_high = 1.5

        info.set_OC_content_low(oc_low)
        info.set_OC_content_high(oc_high)
        info.set_OM_content_low(om_low)
        info.set_OM_content_high(om_high)

        scen.update_scenario(additional_information=[info])

        retrieved_info = scen.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_OC_content_low(), oc_low)
        self.assertEqual(retrieved_info.get_OC_content_high(), oc_high)
        self.assertEqual(retrieved_info.get_OM_content_low(), om_low)
        self.assertEqual(retrieved_info.get_OM_content_high(), om_high)

    def test_organiccontentpartial_oc_additional_information_setters(self):
        scenario_name = self.get_scenario_name()

        scen = Scenario.create(self.pkg, name=scenario_name, description="to test partial OC settings", additional_information=[])

        info = OrganicContentAdditionalInformation()
        oc_low = 1.5

        info.set_OC_content_low(oc_low)

        scen.update_scenario(additional_information=[info])

        retrieved_info = scen.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_OC_content_low(), oc_low)
        self.assertEqual(retrieved_info.get_OC_content_high(), oc_low)
        self.assertIsNone(retrieved_info.get_OM_content_low())
        self.assertIsNone(retrieved_info.get_OM_content_high())

    def test_organiccontentpartial_om_additional_information_setters(self):
        scenario_name = self.get_scenario_name()

        scen = Scenario.create(self.pkg, name=scenario_name, description="to test partial OM settings", additional_information=[])

        info = OrganicContentAdditionalInformation()
        om_high = 1.5

        info.set_OM_content_high(om_high)

        scen.update_scenario(additional_information=[info])

        retrieved_info = scen.get_additional_information()[0]

        self.assertIsNone(retrieved_info.get_OC_content_low())
        self.assertIsNone(retrieved_info.get_OC_content_high())
        self.assertEqual(retrieved_info.get_OM_content_low(), om_high)
        self.assertEqual(retrieved_info.get_OM_content_high(), om_high)

    def test_organiccontent_additional_information_parser(self):
        scenario_name = self.get_scenario_name()

        scen_parser = Scenario.create(self.pkg, name=scenario_name, description="to test organic content additional information parser", additional_information=[])
        data = "1.5 - 3.0;0.5 - 1.5"
        info = OrganicContentAdditionalInformation.parse(data)

        scen_parser.update_scenario(additional_information=[info])

        retrieved_info = scen_parser.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_OC_content_low(), 1.5)
        self.assertEqual(retrieved_info.get_OC_content_high(), 3.0)
        self.assertEqual(retrieved_info.get_OM_content_low(), 0.5)
        self.assertEqual(retrieved_info.get_OM_content_high(), 1.5)

    def test_organiccontentwith_na_additional_information_parser(self):
        scenario_name = self.get_scenario_name()

        scen_parser = Scenario.create(self.pkg, name=scenario_name, description="to test organic content additional information parser with NA values", additional_information=[])
        data = "NA;0.5 - 1.5"
        info = OrganicContentAdditionalInformation.parse(data)

        scen_parser.update_scenario(additional_information=[info])

        retrieved_info = scen_parser.get_additional_information()[0]

        self.assertIsNone(retrieved_info.get_OC_content_low())
        self.assertIsNone(retrieved_info.get_OC_content_high())
        self.assertEqual(retrieved_info.get_OM_content_low(), 0.5)
        self.assertEqual(retrieved_info.get_OM_content_high(), 1.5)

    def test_organiccontentsetters_partial_mixed_additional_information(self):
        scenario_name = self.get_scenario_name()

        scen = Scenario.create(self.pkg, name=scenario_name, description="to test partial mixed OC and OM settings", additional_information=[])

        info = OrganicContentAdditionalInformation()
        oc_high = 3.0
        om_low = 0.5

        info.set_OC_content_high(oc_high)
        info.set_OM_content_low(om_low)

        scen.update_scenario(additional_information=[info])

        retrieved_info = scen.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_OC_content_low(), oc_high)
        self.assertEqual(retrieved_info.get_OC_content_high(), oc_high)
        self.assertEqual(retrieved_info.get_OM_content_low(), om_low)
        self.assertEqual(retrieved_info.get_OM_content_high(), om_low)

    # original sludge amount

    def test_originalsludgeamount_additional_information(self):
        scenario_name = self.get_scenario_name()

        scen = Scenario.create(self.pkg, name=scenario_name, description="to test original sludge amount additional information", additional_information=[])

        info = OriginalSludgeAmountAdditionalInformation()
        sludge_amount = 100.0
        info.set_originalsludgeamount(sludge_amount)

        scen.update_scenario(additional_information=[info])

        retrieved_info = scen.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_originalsludgeamount(), sludge_amount)

    def test_originalsludgeamount_additional_information_parser(self):
        scenario_name = self.get_scenario_name()

        scen_parser = Scenario.create(self.pkg, name=scenario_name, description="to test original sludge amount additional information parser", additional_information=[])
        data = 100.0
        info = OriginalSludgeAmountAdditionalInformation.parse(data)

        scen_parser.update_scenario(additional_information=[info])

        retrieved_info = scen_parser.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_originalsludgeamount(), data)
    
    # oxygen content water sediment
    def test_fulloxygencontent_information(self):
        scenario_name = self.get_scenario_name()

        scen = Scenario.create(self.pkg, name=scenario_name, description="to test oxygen content information", additional_information=[])

        info = OxygenContentWaterSedimentAdditionalInformation()
        info.set_oxygen_content_water_low(5.0)
        info.set_oxygen_content_water_high(8.0)
        info.set_oxygen_content_sediment_low(3.0)
        info.set_oxygen_content_sediment_high(6.0)

        scen.update_scenario(additional_information=[info])

        retrieved_info = scen.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_oxygen_content_water_low(), 5.0)
        self.assertEqual(retrieved_info.get_oxygen_content_water_high(), 8.0)
        self.assertEqual(retrieved_info.get_oxygen_content_sediment_low(), 3.0)
        self.assertEqual(retrieved_info.get_oxygen_content_sediment_high(), 6.0)



    def test_partialnaoxygencontent_information(self):
        scenario_name = self.get_scenario_name()

        scen = Scenario.create(self.pkg, name=scenario_name, description="to test partial NA oxygen content information", additional_information=[])

        info = OxygenContentWaterSedimentAdditionalInformation()
        info.set_oxygen_content_water_high("NA")
        info.set_oxygen_content_sediment_low(3.0)

        scen.update_scenario(additional_information=[info])

        retrieved_info = scen.get_additional_information()[0]

        self.assertIsNone(retrieved_info.get_oxygen_content_water_low())
        self.assertIsNone(retrieved_info.get_oxygen_content_water_high())
        self.assertEqual(retrieved_info.get_oxygen_content_sediment_low(), 3.0)
        self.assertEqual(retrieved_info.get_oxygen_content_sediment_high(), 3.0)

    def test_oxygencontent_information_parser(self):
        scenario_name = self.get_scenario_name()

        scen = Scenario.create(self.pkg, name=scenario_name, description="to test the parser oxygen content information", additional_information=[])

        data = "5.0 - 8.0;3.0 - 6.0"
        info = OxygenContentWaterSedimentAdditionalInformation.parse(data)
        scen.update_scenario(additional_information=[info])

        retrieved_info = scen.get_additional_information()[0]


        self.assertEqual(retrieved_info.get_oxygen_content_water_low(), 5.0)
        self.assertEqual(retrieved_info.get_oxygen_content_water_high(), 8.0)
        self.assertEqual(retrieved_info.get_oxygen_content_sediment_low(), 3.0)
        self.assertEqual(retrieved_info.get_oxygen_content_sediment_high(), 6.0)

    def test_oxygencontent_information_parser_with_na(self):
        scenario_name = self.get_scenario_name()

        scen = Scenario.create(self.pkg, name=scenario_name, description="to test the parser oxygen content information", additional_information=[])

        data = "NA;3.0 - 6.0"
        info = OxygenContentWaterSedimentAdditionalInformation.parse(data)
        scen.update_scenario(additional_information=[info])

        retrieved_info = scen.get_additional_information()[0]



        self.assertIsNone(retrieved_info.get_oxygen_content_water_low())
        self.assertIsNone(retrieved_info.get_oxygen_content_water_high())
        self.assertEqual(retrieved_info.get_oxygen_content_sediment_low(), 3.0)
        self.assertEqual(retrieved_info.get_oxygen_content_sediment_high(), 6.0)
    
    # phosphorus content



    def test_phosphoruscontentinformation(self):
        scenario_name = self.get_scenario_name()
        scen = Scenario.create(self.pkg, name=scenario_name, description="to test phosphorus content information", additional_information=[])

        info = PhosphorusContentAdditionalInformation()
        influent_value = 1.5
        effluent_value = 0.5

        info.set_phosphoruscontentInfluent(influent_value)
        info.set_phosphoruscontentEffluent(effluent_value)

        scen.update_scenario(additional_information=[info])
        retrieved_info = scen.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_phosphoruscontentInfluent(), influent_value)
        self.assertEqual(retrieved_info.get_phosphoruscontentEffluent(), effluent_value)

    def test_phosphoruscontentinformationpartial(self):
        scenario_name = self.get_scenario_name()
        scen = Scenario.create(self.pkg, name=scenario_name, description="to test partial phosphorus content information", additional_information=[])

        info = PhosphorusContentAdditionalInformation()
        influent_value = 1.5

        info.set_phosphoruscontentInfluent(influent_value)

        scen.update_scenario(additional_information=[info])
        retrieved_info = scen.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_phosphoruscontentInfluent(), influent_value)
        self.assertIsNone(retrieved_info.get_phosphoruscontentEffluent())

    def test_phosphoruscontentinformation_parser(self):
        scenario_name = self.get_scenario_name()
        scen = Scenario.create(self.pkg, name=scenario_name, description="to test phosphorus content information parser", additional_information=[])

        data = "1.5;0.5"
        info = PhosphorusContentAdditionalInformation.parse(data)

        scen.update_scenario(additional_information=[info])
        retrieved_info = scen.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_phosphoruscontentInfluent(), 1.5)
        self.assertEqual(retrieved_info.get_phosphoruscontentEffluent(), 0.5)

    def test_phosphoruscontentinformationsingle_parser(self):
        scenario_name = self.get_scenario_name()
        scen = Scenario.create(self.pkg, name=scenario_name, description="to test single phosphorus content information parser", additional_information=[])

        data = "1.5;"
        info = PhosphorusContentAdditionalInformation.parse(data)

        scen.update_scenario(additional_information=[info])
        retrieved_info = scen.get_additional_information()[0]


        self.assertEqual(retrieved_info.get_phosphoruscontentInfluent(), 1.5)
        self.assertIsNone(retrieved_info.get_phosphoruscontentEffluent())

    def test_phosphoruscontentinformationna_parser(self):
        scenario_name = self.get_scenario_name()
        scen = Scenario.create(self.pkg, name=scenario_name, description="to test NA phosphorus content information parser", additional_information=[])

        data = ";0.5"
        info = PhosphorusContentAdditionalInformation.parse(data)

        scen.update_scenario(additional_information=[info])
        retrieved_info = scen.get_additional_information()[0]

        self.assertIsNone(retrieved_info.get_phosphoruscontentInfluent())
        self.assertEqual(retrieved_info.get_phosphoruscontentEffluent(), 0.5)



    # purpose of wwtp

    def test_purposeofwwtsetterandgettervalid(self):
        scenario_name = self.get_scenario_name()
        scen = Scenario.create(self.pkg, name=scenario_name, description="to test purpose of WWTP setter and getter valid", additional_information=[])

        info = PurposeOfWWTPAdditionalInformation()
        valid_values = [
            "municipal WW", "industrial WW", "hospital WW", 
            "mixed WW (municipal & industrial)", "other"
        ]

        for value in valid_values:
            info.set_purposeofwwtp(value)
            scen.update_scenario(additional_information=[info])
            self.assertEqual(info.get_purposeofwwtp(), value)

    def test_purposeofwwtpsetterinvalid(self):
        scenario_name = self.get_scenario_name()
        scen = Scenario.create(self.pkg, name=scenario_name, description="to test purpose of WWTP setter invalid", additional_information=[])

        info = PurposeOfWWTPAdditionalInformation()
        invalid_values = ["residential ww", "commercial ww", "agricultural ww"]

        for value in invalid_values:
            with self.assertRaises(ValueError):
                info.set_purposeofwwtp(value)


    def test_purposeofwwtp_parser(self):
        scenario_name = self.get_scenario_name()
        scen = Scenario.create(self.pkg, name=scenario_name, description="to test purpose of WWTP parser valid", additional_information=[])

        data = "municipal WW"
        info = PurposeOfWWTPAdditionalInformation.parse(data)
        scen.update_scenario(additional_information=[info])
        self.assertEqual(info.get_purposeofwwtp(), data)

        data = "industrial WW"
        info = PurposeOfWWTPAdditionalInformation.parse(data)
        scen.update_scenario(additional_information=[info])
        self.assertEqual(info.get_purposeofwwtp(), data)



    def test_purposeofwwtpinvalidtype_parser(self):
        scenario_name = self.get_scenario_name()
        scen = Scenario.create(self.pkg, name=scenario_name, description="to test purpose of WWTP parser invalid type", additional_information=[])

        data = 12345
        with self.assertRaises(ValueError):
            PurposeOfWWTPAdditionalInformation.parse(data)

    # rate constant


    def test_rateconstant_information(self):
        scenario_name = self.get_scenario_name()
        info = RateConstantAdditionalInformation()
        lower_value = 0.1
        upper_value = 0.5
        order_value = "First order"
        corrected_value = "sorption corrected"
        comment_value = "Test comment"

        scen = Scenario.create(self.pkg, name=scenario_name, description="to test rate constant",
                               additional_information=[])

        info.set_rateconstantlower(lower_value)
        info.set_rateconstantupper(upper_value)
        info.set_rateconstantorder(order_value)
        info.set_rateconstantcorrected(corrected_value)
        info.set_rateconstantcomment(comment_value)

        scen.update_scenario(additional_information=[info])
        
        retrieved_info = scen.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_rateconstantlower(), lower_value)
        self.assertEqual(retrieved_info.get_rateconstantupper(), upper_value)
        self.assertEqual(retrieved_info.get_rateconstantorder(), order_value)
        self.assertEqual(retrieved_info.get_rateconstantcorrected(), corrected_value)
        self.assertEqual(retrieved_info.get_rateconstantcomment(), comment_value)



    def test_rateconstant_information_parser(self):
        scenario_name = self.get_scenario_name()
        data_string = "First order;sorption corrected;0.1 - 0.5;Test comment"
        info = RateConstantAdditionalInformation.parse(data_string)

        scen = Scenario.create(self.pkg, name=scenario_name, description="to test rate constant parser",
                               additional_information=[])

        scen.update_scenario(additional_information=[info])
        retrieved_info = scen.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_rateconstantorder(), "First order")
        self.assertEqual(retrieved_info.get_rateconstantcorrected(), "sorption corrected")
        self.assertEqual(retrieved_info.get_rateconstantlower(), 0.1)
        self.assertEqual(retrieved_info.get_rateconstantupper(), 0.5)
        self.assertEqual(retrieved_info.get_rateconstantcomment(), "Test comment")



    # redox 

    def test_redoxsetterandgettervalid(self):
        
        info = RedoxAdditionalInformation()

        valid_types = ['aerob', 'anaerob', 'anaerob: iron-reducing', 'anaerob: sulfate-reducing',
                       'anaerob: methanogenic conditions', 'oxic', 'nitrate-reducing']

        for redox_type in valid_types:
            scen = Scenario.create(self.pkg, name=redox_type, description="to test redox", additional_information=[])

            info.set_redoxType(redox_type)
            scen.update_scenario(additional_information=[info])
            retrieved_info = scen.get_additional_information()[0]
            self.assertEqual(retrieved_info.get_redoxType(), redox_type)

    def test_redoxsetterinvalid(self):
        info = RedoxAdditionalInformation()

        invalid_types = ['oxidative', 'anaerobic: sulfur-reducing', 'oxic: high oxygen']

        for redox_type in invalid_types:
            scen = Scenario.create(self.pkg, name=redox_type, description="to test redox", additional_information=[])

            with self.assertRaises(ValueError):
                info.set_redoxType(redox_type)
                scen.update_scenario(additional_information=[info])

    def test_redox_parser(self):
        scenario_name = self.get_scenario_name()
        data_string = "aerob"
        info = RedoxAdditionalInformation.parse(data_string)

        scen = Scenario.create(self.pkg, name=scenario_name, description="to test redox", additional_information=[])

        
        scen.update_scenario(additional_information=[info])
        retrieved_info = scen.get_additional_information()[0]
        self.assertEqual(retrieved_info.get_redoxType(), "aerob")

    def test_parser_invalid(self):
        # Test parsing with invalid data
        with self.assertRaises(ValueError):
            RedoxAdditionalInformation.parse("invalid_redox_type")



    # redox potential

    def test_redoxpotentialsetterandgetter(self):
        scenario_name = self.get_scenario_name()
        info = RedoxPotentialAdditionalInformation()

        # Valid values
        valid_low_water = 100.0
        valid_high_water = 300.0
        valid_low_sediment = -200.0
        valid_high_sediment = 100.0

        
        scen = Scenario.create(self.pkg, name=scenario_name, description="to test redox potential",
                               additional_information=[])

        
        info.set_lowPotentialWater(valid_low_water)
        info.set_highPotentialWater(valid_high_water)
        info.set_lowPotentialSediment(valid_low_sediment)
        info.set_highPotentialSediment(valid_high_sediment)
        scen.update_scenario(additional_information=[info])

        retrieved_info = scen.get_additional_information()[0]
        self.assertEqual(retrieved_info.get_lowPotentialWater(), valid_low_water)
        self.assertEqual(retrieved_info.get_highPotentialWater(), valid_high_water)
        self.assertEqual(retrieved_info.get_lowPotentialSediment(), valid_low_sediment)
        self.assertEqual(retrieved_info.get_highPotentialSediment(), valid_high_sediment)

    def test_redoxpotential_parser(self):
        scenario_name = self.get_scenario_name()
        data_string = "100.0 - 300.0;-200.0 - 100.0"
        info = RedoxPotentialAdditionalInformation.parse(data_string)

        
        scen = Scenario.create(self.pkg, name=scenario_name, description="to test redox potential",
                               additional_information=[])

        
        scen.update_scenario(additional_information=[info])
        retrieved_info = scen.get_additional_information()[0]
        self.assertEqual(retrieved_info.get_lowPotentialWater(), 100.0)
        self.assertEqual(retrieved_info.get_highPotentialWater(), 300.0)
        self.assertEqual(retrieved_info.get_lowPotentialSediment(), -200.0)
        self.assertEqual(retrieved_info.get_highPotentialSediment(), 100.0)



    # reference 


    def test_referencesetterandgetter_valid(self):
        scenario_name = self.get_scenario_name()
        info = ReferenceAdditionalInformation()

        # Valid value
        valid_reference = "123456"

        
        scen = Scenario.create(self.pkg, name=scenario_name, description="to test reference",
                               additional_information=[])

        
        info.set_reference(valid_reference)
        scen.update_scenario(additional_information=[info])

        retrieved_info = scen.get_additional_information()[0]
        self.assertEqual(retrieved_info.get_reference(), valid_reference)

    def test_reference_parser(self):
        scenario_name = self.get_scenario_name()
        data_string = "123456"
        info = ReferenceAdditionalInformation.parse(data_string)

        
        scen = Scenario.create(self.pkg, name=scenario_name, description="to test reference",
                               additional_information=[])

        
        scen.update_scenario(additional_information=[info])
        retrieved_info = scen.get_additional_information()[0]
        self.assertEqual(retrieved_info.get_reference(), "123456")

    # sampling depth

    def test_samplingdepthsetterandgetter(self):
        scenario_name = self.get_scenario_name()
        info = SamplingDepthAdditionalInformation()

        # Valid values
        valid_min_depth = 10.0
        valid_max_depth = 20.0

        
        scen = Scenario.create(self.pkg, name=scenario_name, description="to test sampling depth",
                               additional_information=[])

        
        info.set_samplingDepthMin(valid_min_depth)
        info.set_samplingDepthMax(valid_max_depth)
        scen.update_scenario(additional_information=[info])

        retrieved_info = scen.get_additional_information()[0]
        self.assertEqual(retrieved_info.get_samplingDepthMin(), valid_min_depth)
        self.assertEqual(retrieved_info.get_samplingDepthMax(), valid_max_depth)

    def test_samplingdepth_parser(self):
        scenario_name = self.get_scenario_name()
        data_string = "10.0;20.0"
        info = SamplingDepthAdditionalInformation.parse(data_string)

        
        scen = Scenario.create(self.pkg, name=scenario_name, description="to test sampling depth",
                               additional_information=[])

        
        scen.update_scenario(additional_information=[info])
        retrieved_info = scen.get_additional_information()[0]
        self.assertEqual(retrieved_info.get_samplingDepthMin(), 10.0)
        self.assertEqual(retrieved_info.get_samplingDepthMax(), 20.0)

    def test_samplingdepthsingle_value_parser(self):
        scenario_name = self.get_scenario_name()
        data_string = "10.0"
        info = SamplingDepthAdditionalInformation.parse(data_string)

        
        scen = Scenario.create(self.pkg, name=scenario_name, description="to test sampling depth",
                               additional_information=[])

        
        scen.update_scenario(additional_information=[info])
        retrieved_info = scen.get_additional_information()[0]
        self.assertEqual(retrieved_info.get_samplingDepthMin(), 10.0)
        self.assertEqual(retrieved_info.get_samplingDepthMax(), 10.0)

    # sediment porosity

    def test_sedimentporosity_information(self):
        scenario_name = self.get_scenario_name()
        info = SedimentPorosityAdditionalInformation()
        porosity_value = 0.45

        
        scen = Scenario.create(self.pkg, name=scenario_name, description="to test sediment porosity",
                               additional_information=[])

        info.set_sedimentporosity(porosity_value)

        
        scen.update_scenario(additional_information=[info])
        retrieved_info = scen.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_sedimentporosity(), porosity_value)


    def test_sedimentporosity_information_parser(self):
        scenario_name = self.get_scenario_name()
        data_string = "0.45"
        info = SedimentPorosityAdditionalInformation.parse(data_string)

        
        scen = Scenario.create(self.pkg, name=scenario_name, description="to test sediment porosity parser",
                               additional_information=[])

        
        scen.update_scenario(additional_information=[info])
        retrieved_info = scen.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_sedimentporosity(), 0.45)


    # sludge retention time

    def test_sludgeretentiontime_information(self):
        scenario_name = self.get_scenario_name()
        info = SludgeRetentionTimeAdditionalInformation()
        retention_time_type = "sludge age"
        retention_time_value = 10.5

        
        scen = Scenario.create(self.pkg, name=scenario_name, description="to test sludge retention time",
                               additional_information=[])

        info.set_sludgeretentiontimeType(retention_time_type)
        info.set_sludgeretentiontime(retention_time_value)

        
        scen.update_scenario(additional_information=[info])
        retrieved_info = scen.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_sludgeretentiontimeType(), retention_time_type)
        self.assertEqual(retrieved_info.get_sludgeretentiontime(), retention_time_value)



    def test_sludgeretentiontime_information_parser(self):
        scenario_name = self.get_scenario_name()
        data_string = "sludge age;10.5"
        info = SludgeRetentionTimeAdditionalInformation.parse(data_string)

        
        scen = Scenario.create(self.pkg, name=scenario_name, description="to test sludge retention time parser",
                               additional_information=[])

        
        scen.update_scenario(additional_information=[info])
        retrieved_info = scen.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_sludgeretentiontimeType(), "sludge age")
        self.assertEqual(retrieved_info.get_sludgeretentiontime(), 10.5)

    def test_sludgeretentiontime_information_parser_invalid(self):
        data_string = "invalid_type;10.5"
        with self.assertRaises(ValueError):
            SludgeRetentionTimeAdditionalInformation.parse(data_string)

    def test_sludgeretentiontime_information_parser_type_error(self):
        data_string = "sludge age;not_a_float"
        with self.assertRaises(ValueError):
            SludgeRetentionTimeAdditionalInformation.parse(data_string)

    # soil classification system
    def test_soilclassificationsystem_information(self):
        info = SoilClassificationAdditionalInformation()
        classification_system = "USDA"

        
        scen = Scenario.create(self.pkg, name=self.get_scenario_name(), description="to test soil classification system",
                               additional_information=[])

        info.set_soilclassificationsystem(classification_system)

        
        scen.update_scenario(additional_information=[info])
        retrieved_info = scen.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_soilclassificationsystem(), classification_system)



    def test_soilclassificationsystem_information_parser(self):
        data_string = "USDA"
        info = SoilClassificationAdditionalInformation.parse(data_string)

        
        scen = Scenario.create(self.pkg, name=self.get_scenario_name(), description="to test soil classification system parser",
                               additional_information=[])

        
        scen.update_scenario(additional_information=[info])
        retrieved_info = scen.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_soilclassificationsystem(), "USDA")

    def test_soilclassificationsystem_information_parser_invalid(self):
        data_string = "invalid_system"
        with self.assertRaises(ValueError):
            SoilClassificationAdditionalInformation.parse(data_string)



    # soil source

    def test_soilsourcedata_information(self):
        info = SoilSourceAdditionalInformation()
        soil_source_data = "Magden"

        
        scen = Scenario.create(self.pkg, name=self.get_scenario_name(), description="to test soil source data",
                               additional_information=[])

        info.set_soilsourcedata(soil_source_data)

        
        scen.update_scenario(additional_information=[info])
        retrieved_info = scen.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_soilsourcedata(), soil_source_data)



    def test_soilsourcedata_information_parser(self):
        data_string = "Field A"
        info = SoilSourceAdditionalInformation.parse(data_string)

        
        scen = Scenario.create(self.pkg, name=self.get_scenario_name(), description="to test soil source data parser",
                               additional_information=[])

        
        scen.update_scenario(additional_information=[info])
        retrieved_info = scen.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_soilsourcedata(), "Field A")



    # soil texture type
    
    def test_soilclassificationsystem_information(self):
        allowed_types = ["USDA", "UK_ADAS", "UK", "DE", "International"]
        for soil_classification_type in allowed_types:
            info = SoilClassificationAdditionalInformation()

            
            scen = Scenario.create(self.pkg, name=self.get_scenario_name(), description=f"to test soil classification: {soil_classification_type}",
                                   additional_information=[])

            info.set_soilclassificationsystem(soil_classification_type)

            
            scen.update_scenario(additional_information=[info])
            retrieved_info = scen.get_additional_information()[0]
            if soil_classification_type == "UK_ADAS":
                self.assertEqual(retrieved_info.get_soilclassificationsystem(), "UK ADAS")
            else:
                self.assertEqual(retrieved_info.get_soilclassificationsystem(), soil_classification_type)

    def test_soilclassificationsysteminvalid_information(self):
        invalid_types = ["Invalid", "Type"]
        for soil_classification_type in invalid_types:
            info = SoilClassificationAdditionalInformation()

            
            scen = Scenario.create(self.pkg, name=self.get_scenario_name(), description=f"to test invalid soil classification: {soil_classification_type}",
                                   additional_information=[])

            # Try setting invalid type
            with self.assertRaises(ValueError):
                info.set_soilclassificationsystem(soil_classification_type)


    def test_soilclassificationsystem_information_parser(self):
        data_string = "USDA"
        info = SoilClassificationAdditionalInformation.parse(data_string)

        
        scen = Scenario.create(self.pkg, name=self.get_scenario_name(), description="to test soil classification parser",
                               additional_information=[])

        
        scen.update_scenario(additional_information=[info])
        retrieved_info = scen.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_soilclassificationsystem(), "USDA")

    def test_soilclassificationsystem_information_parser_invalid(self):
        data_string = "Invalid"
        with self.assertRaises(ValueError):
            SoilClassificationAdditionalInformation.parse(data_string)


    # soil texture 2

    def test_soiltexture2_information(self):
        test_data = [
            {"sand": 45.0, "silt": 34.0, "clay": 21.0},
            {"sand": 20.0, "silt": 50.0, "clay": 30.0},
            {"sand": 10.0, "silt": 30.0, "clay": 60.0}
        ]

        for data in test_data:
            info = SoilTexture2AdditionalInformation()

            
            scen = Scenario.create(self.pkg, name=self.get_scenario_name(), description="to test soil texture 2",
                                   additional_information=[])

            
            info.set_sand(data["sand"])
            info.set_silt(data["silt"])
            info.set_clay(data["clay"])

            
            scen.update_scenario(additional_information=[info])
            retrieved_info = scen.get_additional_information()[0]

            self.assertEqual(retrieved_info.get_sand(), data["sand"])
            self.assertEqual(retrieved_info.get_silt(), data["silt"])
            self.assertEqual(retrieved_info.get_clay(), data["clay"])

    def test_soiltexture2_information_parser(self):
        data_string = "Soil texture 2: 45.0% sand; 34.0% silt; 21.0% clay"
        info = SoilTexture2AdditionalInformation.parse(data_string)

        
        scen = Scenario.create(self.pkg, name=self.get_scenario_name(), description="to test soil texture 2 parser",
                               additional_information=[])

        
        scen.update_scenario(additional_information=[info])
        retrieved_info = scen.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_sand(), 45.0)
        self.assertEqual(retrieved_info.get_silt(), 34.0)
        self.assertEqual(retrieved_info.get_clay(), 21.0)


    # source scenario

    def test_sourcescenario_information(self):
        test_data = "https://envipath.org/package/57c34a2f-6310-49b1-92df-a50b5f055d6e/scenario/f844990a-6944-4677-9287-8550999ce672"

    
        info = SourceScenarioAdditionalInformation()

        
        scen = Scenario.create(self.pkg, name=self.get_scenario_name(), description="to test source scenario",
                                additional_information=[])

        info.set_sourcescenario(test_data)

        
        scen.update_scenario(additional_information=[info])
        retrieved_info = scen.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_sourcescenario(), "http[64 chars]enario/f844990a-6944-4677-9287-8550999ce672;Aeration - (00012)")

    def test_sourcescenario_information_parser(self):
        data_string = "https://envipath.org/package/57c34a2f-6310-49b1-92df-a50b5f055d6e/scenario/f844990a-6944-4677-9287-8550999ce672"
        info = SourceScenarioAdditionalInformation.parse(data_string)

        
        scen = Scenario.create(self.pkg, name=self.get_scenario_name(), description="to test source scenario parser",
                               additional_information=[])

        
        scen.update_scenario(additional_information=[info])
        retrieved_info = scen.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_sourcescenario(), "https://envipath.org/package/57c34a2f-6310-49b1-92df-a50b5f055d6e/scenario/f844990a-6944-4677-9287-8550999ce672;Aeration - (00012)")


    # spike compound
    def test_spikecompoundsetter_and_getter(self):
        scenario_name = self.get_scenario_name()
        
        scen = Scenario.create(self.pkg, name=scenario_name, description="Test setter and getter", additional_information=[])

        info = SpikeCompoundAdditionalInformation()
        
        info.set_spikeComp("https://envipath.org/package/57c34a2f-6310-49b1-92df-a50b5f055d6e/compound/1a719d31-643b-46bc-93d7-25039f1d8c44/structure/6f6021ec-ef10-4593-8bd0-438267a2d520")
        scen.update_scenario(additional_information=[info])
        retrieved_info = scen.get_additional_information()[0]
        self.assertEqual(retrieved_info.get_spikeComp(), "structure 0000001")

        info.set_spikeComp("C1=CC=CC=C1")  # example SMILE
        scen.update_scenario(additional_information=[info])
        retrieved_info = scen.get_additional_information()[0]
        self.assertEqual(retrieved_info.get_spikeComp(), "structure 0000001")

    def test_spikecompound_parser(self):
        scenario_name = self.get_scenario_name()
        
        scen = Scenario.create(self.pkg, name=scenario_name, description="Test parser", additional_information=[])
        
        data_string = "https://envipath.org/package/57c34a2f-6310-49b1-92df-a50b5f055d6e/compound/1a719d31-643b-46bc-93d7-25039f1d8c44/structure/6f6021ec-ef10-4593-8bd0-438267a2d520"
        info = SpikeCompoundAdditionalInformation.parse(data_string)
        scen.update_scenario(additional_information=[info])
        retrieved_info = scen.get_additional_information()[0]
        self.assertEqual(retrieved_info.get_spikeComp(), "structure 0000001")

        data_string = "C1=CC=CC=C1"  # example SMILE
        info = SpikeCompoundAdditionalInformation.parse(data_string)
        scen.update_scenario(additional_information=[info])
        retrieved_info = scen.get_additional_information()[0]
        self.assertEqual(retrieved_info.get_spikeComp(), "structure 0000001")

    # spike concentration

    def test_spikeconcentrationsetter_and_getter(self):
        scenario_name = self.get_scenario_name()
        
        scen = Scenario.create(self.pkg, name=scenario_name, description="Test setter and getter", additional_information=[])

        info = SpikeConcentrationAdditionalInformation()
        
        info.set_spikeConcentration(10.5)

        for unit in SpikeConcentrationAdditionalInformation.valid_units:
            info.set_spikeconcentrationUnit(unit)
            scen.update_scenario(additional_information=[info])
            retrieved_info = scen.get_additional_information()[0]
            self.assertEqual(retrieved_info.get_spikeconcentrationUnit(), unit)
            self.assertEqual(retrieved_info.get_spikeConcentration(), 10.5)

    def test_spikeconcententrationsetterinvalid_value(self):
        scenario_name = self.get_scenario_name()
        
        scen = Scenario.create(self.pkg, name=scenario_name, description="Test setter invalid value", additional_information=[])
        info = SpikeConcentrationAdditionalInformation()
        
        with self.assertRaises(ValueError):
            info.set_spikeConcentration("not_a_float")  

        with self.assertRaises(ValueError):
            info.set_spikeconcentrationUnit("INVALID_UNIT")  

    def test_spikeconcentration_parser(self):
        scenario_name = self.get_scenario_name()
        
        scen = Scenario.create(self.pkg, name=scenario_name, description="Test parser", additional_information=[])
        
        
        data_string = "10.5"
        info = SpikeConcentrationAdditionalInformation.parse(data_string)
        scen.update_scenario(additional_information=[info])
        retrieved_info = scen.get_additional_information()[0]
        self.assertEqual(retrieved_info.get_spikeConcentration(), 10.5)
        



    # temperature
    def test_temperature_information(self):
        
        test_data = [
            {"temperatureMin": 10.5, "temperatureMax": 20.5},
            {"temperatureMin": 5.0, "temperatureMax": 25.0},
            {"temperatureMin": -5.0, "temperatureMax": 15.0}
        ]

        for data in test_data:
            info = TemperatureAdditionalInformation()

            
            scen = Scenario.create(self.pkg, name=self.get_scenario_name(), description="to test temperature",
                                   additional_information=[])

            info.set_temperatureMin(data["temperatureMin"])
            info.set_temperatureMax(data["temperatureMax"])

            
            scen.update_scenario(additional_information=[info])
            retrieved_info = scen.get_additional_information()[0]

            self.assertEqual(retrieved_info.get_temperatureMin(), data["temperatureMin"])
            self.assertEqual(retrieved_info.get_temperatureMax(), data["temperatureMax"])

    def test_temperature_information_parser(self):
        data_string = "5.0;25.0"
        info = TemperatureAdditionalInformation.parse(data_string)

        
        scen = Scenario.create(self.pkg, name=self.get_scenario_name(), description="to test temperature parser",
                               additional_information=[])

        
        scen.update_scenario(additional_information=[info])
        retrieved_info = scen.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_temperatureMin(), 5.0)
        self.assertEqual(retrieved_info.get_temperatureMax(), 25.0)

    # total organic carbon (TOC)

    def test_total_organic_carbon_information(self):
        test_data = [
            {"totalorganiccarbonStart": 5.0, "totalorganiccarbonEnd": 15.0},
            {"totalorganiccarbonStart": 2.5, "totalorganiccarbonEnd": 10.0},
            {"totalorganiccarbonStart": 0.0, "totalorganiccarbonEnd": 20.0}
        ]

        for data in test_data:
            info = TotalOrganicCarbonAdditionalInformation()

            
            scen = Scenario.create(self.pkg, name=self.get_scenario_name(), description="to test total organic carbon",
                                   additional_information=[])

            info.set_totalorganiccarbonStart(data["totalorganiccarbonStart"])
            info.set_totalorganiccarbonEnd(data["totalorganiccarbonEnd"])

            
            scen.update_scenario(additional_information=[info])
            retrieved_info = scen.get_additional_information()[0]

            self.assertEqual(retrieved_info.get_totalorganiccarbonStart(), data["totalorganiccarbonStart"])
            self.assertEqual(retrieved_info.get_totalorganiccarbonEnd(), data["totalorganiccarbonEnd"])

    def test_total_organic_carbon_information_parser(self):
        data_string = "2.5;10.0"
        info = TotalOrganicCarbonAdditionalInformation.parse(data_string)

        
        scen = Scenario.create(self.pkg, name=self.get_scenario_name(), description="to test total organic carbon parser",
                               additional_information=[])

        
        scen.update_scenario(additional_information=[info])
        retrieved_info = scen.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_totalorganiccarbonStart(), 2.5)
        self.assertEqual(retrieved_info.get_totalorganiccarbonEnd(), 10.0)


    # tss

    def test_tss_information(self):
        
        info = TSSAdditionalInformation()

        scen = Scenario.create(self.pkg, name=self.get_scenario_name(), description="to test TSS",
                                additional_information=[])

        info.set_ttsStart(8.0)
        info.set_ttsEnd(12.0)

        
        scen.update_scenario(additional_information=[info])
        retrieved_info = scen.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_ttsStart(), 8.0)
        self.assertEqual(retrieved_info.get_ttsEnd(), 12.0)

    def test_tss_information_parser(self):
        data_string = "2.5 - 10.0"
        info = TSSAdditionalInformation.parse(data_string)

        
        scen = Scenario.create(self.pkg, name=self.get_scenario_name(), description="to test TSS parser",
                               additional_information=[])

        
        scen.update_scenario(additional_information=[info])
        retrieved_info = scen.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_ttsStart(), 2.5)
        self.assertEqual(retrieved_info.get_ttsEnd(), 10.0)

    # type of compound addition
    def test_typeofaddition_information(self):
        test_data = [
            "spiking in solvent",
            "plating",
            "other"
        ]

        for data in test_data:
            info = TypeOfAdditionAdditionalInformation()

            
            scen = Scenario.create(self.pkg, name=self.get_scenario_name(), description="to test Type of Addition",
                                   additional_information=[])

            info.set_typeofaddition(data)

            
            scen.update_scenario(additional_information=[info])
            retrieved_info = scen.get_additional_information()[0]

            self.assertEqual(retrieved_info.get_typeofaddition(), data)

    def test_typeofaddition_information_parser(self):
        data_string = "spiking in solvent"
        info = TypeOfAdditionAdditionalInformation.parse(data_string)

        
        scen = Scenario.create(self.pkg, name=self.get_scenario_name(), description="to test Type of Addition parser",
                               additional_information=[])

        
        scen.update_scenario(additional_information=[info])
        retrieved_info = scen.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_typeofaddition(), "spiking in solvent")



    # type of aeration

    def test_typeofaeration_information(self):
        test_data = [
            "stirring",
            "shaking",
            "bubbling air",
            "bubbling air and stirring",
            "other"
        ]

        for data in test_data:
            info = TypeOfAerationAdditionalInformation()

            
            scen = Scenario.create(self.pkg, name=self.get_scenario_name(), description="to test Type of Aeration",
                                   additional_information=[])

            info.set_typeofaeration(data)

            
            scen.update_scenario(additional_information=[info])
            retrieved_info = scen.get_additional_information()[0]

            self.assertEqual(retrieved_info.get_typeofaeration(), data)

    def test_typeofaeration_information_parser(self):
        data_string = "stirring"
        info = TypeOfAerationAdditionalInformation.parse(data_string)

        
        scen = Scenario.create(self.pkg, name=self.get_scenario_name(), description="to test Type of Aeration parser",
                               additional_information=[])

        
        scen.update_scenario(additional_information=[info])
        retrieved_info = scen.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_typeofaeration(), "stirring")

    def test_invalid_typeofaeration(self):
        with self.assertRaises(ValueError):
            TypeOfAerationAdditionalInformation().set_typeofaeration("invalid type")
   
    # volatile tss
    def test_volatiletts_information(self):
        test_data = [
            ("10.5", "20.5"),
            ("15.2", None),
            (None, "25.3"),
        ]

        for start, end in test_data:
            info = VolatileTSSAdditionalInformation()

            
            scen = Scenario.create(self.pkg, name=self.get_scenario_name(), description="to test Volatile TSS",
                                   additional_information=[])

            if start:
                info.set_volatilettsStart(float(start))
            if end:
                info.set_volatilettsEnd(float(end))

            
            scen.update_scenario(additional_information=[info])
            retrieved_info = scen.get_additional_information()[0]

            self.assertEqual(retrieved_info.get_volatilettsStart(), float(start) if start else float(end))
            self.assertEqual(retrieved_info.get_volatilettsEnd(), float(end) if end else float(start))

    def test_volatiletts_information_parser(self):
        data_string = "10.5 - 20.5"
        info = VolatileTSSAdditionalInformation.parse(data_string)

        
        scen = Scenario.create(self.pkg, name=self.get_scenario_name(), description="to test Volatile TSS parser",
                               additional_information=[])

        
        scen.update_scenario(additional_information=[info])
        retrieved_info = scen.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_volatilettsStart(), 10.5)
        self.assertEqual(retrieved_info.get_volatilettsEnd(), 20.5)

    def test_invalid_volatiletts(self):
        with self.assertRaises(TypeError):
            VolatileTSSAdditionalInformation().set_volatilettsStart("invalid value")
    
    # water storage capacity
    def test_waterstoragecapacity_information(self):

        info = WaterStorageCapacityAdditionalInformation()

        
        scen = Scenario.create(self.pkg, name=self.get_scenario_name(), description="to test Water Storage Capacity",
                                additional_information=[])

        
        info.set_wst(10.5)
        info.set_wstConditions("0.1 bar = pF2.0")
        info.set_maximumWaterstoragecapacity(20.5)

        
        scen.update_scenario(additional_information=[info])
        retrieved_info = scen.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_wst(), 10.5)
        self.assertEqual(retrieved_info.get_wstConditions(),"0.1 bar = pF2.0")
        self.assertEqual(retrieved_info.get_maximumWaterstoragecapacity(), 20.5)

    def test_waterstoragecapacity_information_parser(self):
        data_string = "10.5 - 0.1 bar = pF2.0 - 20.5"
        info = WaterStorageCapacityAdditionalInformation.parse(data_string)

        
        scen = Scenario.create(self.pkg, name=self.get_scenario_name(), description="to test Water Storage Capacity parser",
                               additional_information=[])

        
        scen.update_scenario(additional_information=[info])
        retrieved_info = scen.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_wst(), 10.5)
        self.assertEqual(retrieved_info.get_wstConditions(), "0.1 bar = pF2.0")
        self.assertEqual(retrieved_info.get_maximumWaterstoragecapacity(), 20.5)

    def test_invalid_water_storage_capacity(self):
        with self.assertRaises(ValueError):
            WaterStorageCapacityAdditionalInformation().set_wst("invalid value")


    # parameters measured

    def test_parametersetter_and_getter(self):
        # Test setter and getter for each parameter
        valid_parameters = [
            "NH4+", "NH4-", "NH4-N", "NO3-",
            "NO2-", "Ntot", "PO43-",
            "P-tot", "DOC", "none", "NH&#8324&#8314", "NH&#8324&#8315","NH&#8324-N",
            "NO&#8323&#8315","NO&#8322&#8315","N&#8348&#8338&#8348",
            "PO&#8324&#179&#8315","P&#8348&#8338&#8348"
        ]
        
        for param in ["NH4+", "NH4-", "NH4-N", "NO3-", "NO2-", "Ntot", "PO43-", "P-tot", "DOC", "none"]:
            scenario_name = param
            scen = Scenario.create(self.pkg, name=scenario_name, description="Test setter and getter", additional_information=[])

            info = ParametersMeasuredAdditionalInformation()
            info.set_addparametersmeasured(param)
            scen.update_scenario(additional_information=[info])

            retrieved_info = scen.get_additional_information()[0]
            self.assertIn(retrieved_info.get_addparametersmeasured(),valid_parameters)

    def test_parameter_parser(self):
        
        valid_parameters = [
            "NH4+", "NH4-", "NH4-N", "NO3-",
            "NO2-", "Ntot", "PO43-",
            "P-tot", "DOC", "none", "NH&#8324&#8314","NH&#8324&#8315","NH&#8324-N",
            "NO&#8323&#8315","NO&#8322&#8315","N&#8348&#8338&#8348",
            "PO&#8324&#179&#8315","P&#8348&#8338&#8348"
        ]
        for param in ["NH4+", "NH4-", "NH4-N", "NO3-", "NO2-", "Ntot", "PO43-", "P-tot", "DOC", "none"]:
            scenario_name = param
            scen = Scenario.create(self.pkg, name=scenario_name, description="Test parser", additional_information=[])

            data_string = param
            info = ParametersMeasuredAdditionalInformation.parse(data_string)
            scen.update_scenario(additional_information=[info])

            retrieved_info = scen.get_additional_information()[0]
            

            self.assertIn(retrieved_info.get_addparametersmeasured(),valid_parameters)



    # Oxygen Demand

    def test_oxygendemand_additional_information(self):
        scenario_name = self.get_scenario_name()
        
        scen = Scenario.create(self.pkg, name=scenario_name,description="to test",additional_information= [])

        oxdem = OxygenDemandAdditionalInformation()
        oxdem.set_oxygendemandType("Chemical Oxygen Demand (COD)")
        oxdem.set_oxygendemandInfluent(300.0)
        oxdem.set_oxygendemandEffluent(100.0)

        scen.update_scenario(additional_information=[oxdem])

        retrieved_info = scen.get_additional_information()[0]

       
        self.assertEqual(retrieved_info.get_oxygendemandType(), "Chemical Oxygen Demand (COD)")
        self.assertEqual(retrieved_info.get_oxygendemandInfluent(), 300.0)
        self.assertEqual(retrieved_info.get_oxygendemandEffluent(), 100.0)

    def test_oxygendemand_parser(self):
        scenario_name = self.get_scenario_name()
        scen_parser = Scenario.create(self.pkg,name=scenario_name,description="to test",additional_information= [])
        data = "Chemical Oxygen Demand (COD);300.0;100.0"
        info = OxygenDemandAdditionalInformation.parse(data)
    
        scen_parser.update_scenario(additional_information=[info])

        retrieved_info = scen_parser.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_oxygendemandType(), "Chemical Oxygen Demand (COD)")
        self.assertEqual(retrieved_info.get_oxygendemandInfluent(), 300.0)
        self.assertEqual(retrieved_info.get_oxygendemandEffluent(), 100.0)

    # Dissolved Oxygen

    def test_dissolvedoxygenconcentration_additional_information(self):
        scenario_name = self.get_scenario_name()
        scen = Scenario.create(self.pkg, name=scenario_name, description="to test", additional_information=[])
        disox = DissolvedOxygenConcentrationAdditionalInformation()
        disox.set_DissolvedoxygenconcentrationLow(2.0)
        disox.set_DissolvedoxygenconcentrationHigh(8.0)

        scen.update_scenario(additional_information=[disox])

        retrieved_info = scen.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_DissolvedoxygenconcentrationLow(), 2.0)
        self.assertEqual(retrieved_info.get_DissolvedoxygenconcentrationHigh(), 8.0)

    def test_dissolvedoxygenconcentration_parser(self):
        scenario_name = self.get_scenario_name()
        scen_parser = Scenario.create(self.pkg,name=scenario_name,description="to test",additional_information= [])
        dissolved_oxygen_data = "2.0;8.0"
        dissolved_oxygen_info = DissolvedOxygenConcentrationAdditionalInformation.parse(dissolved_oxygen_data)

        
        scen_parser.update_scenario(additional_information=[dissolved_oxygen_info])

        retrieved_info = scen_parser.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_DissolvedoxygenconcentrationLow(), 2.0)
        self.assertEqual(retrieved_info.get_DissolvedoxygenconcentrationHigh(), 8.0)


    # oxygen uptake rate

    def test_OxygenUptakeRate_AdditionalInformation(self):
        scenario_name = self.get_scenario_name()
        scen = Scenario.create(self.pkg, name=scenario_name, description="to test", additional_information=[])
        oxup = OxygenUptakeRateAdditionalInformation()        
        oxup.set_oxygenuptakerateStart(20.0)
        oxup.set_oxygenuptakerateEnd(30.0)

        scen.update_scenario(additional_information=[oxup])

        retrieved_info = scen.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_oxygenuptakerateStart(), 20.0)
        self.assertEqual(retrieved_info.get_oxygenuptakerateEnd(), 30.0)

    def test_OxygenUptakeRate_parser(self):
        scenario_name = self.get_scenario_name()
        scen_parser = Scenario.create(self.pkg,name=scenario_name,description="to test",additional_information= [])
        data = "2.0;8.0"
        info = OxygenUptakeRateAdditionalInformation.parse(data)

        scen_parser.update_scenario(additional_information=[info])

        retrieved_info = scen_parser.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_oxygenuptakerateStart(), 2.0)
        self.assertEqual(retrieved_info.get_oxygenuptakerateEnd(), 8.0)

    # aeration type 
    def test_AerationType_AdditionalInformation(self):
        scenario_name = self.get_scenario_name()
        allowed_values = ["stirring", "shaking", "bubbling air", "bubbling air and stirring", "other"]
        
        for value in allowed_values:
            scen = Scenario.create(self.pkg, name=scenario_name, description="to test", additional_information=[])
            info = AerationTypeAdditionalInformation()
            info.set_aerationtype(value)

            scen.update_scenario(additional_information=[info])

            retrieved_info = scen.get_additional_information()[0]

            self.assertEqual(retrieved_info.get_aerationtype(), value)



    def test_AerationType_AdditionalInformation_parser(self):
        scenario_name = self.get_scenario_name()
        allowed_values = ["stirring", "shaking", "bubbling air", "bubbling air and stirring", "other"]
        
        for value in allowed_values:
            scen_parser = Scenario.create(self.pkg,name=scenario_name,description="to test",additional_information= [])
            data = value
            info = AerationTypeAdditionalInformation.parse(data)
            info.set_aerationtype(value)

            scen_parser.update_scenario(additional_information=[info])

            retrieved_info = scen_parser.get_additional_information()[0]

            self.assertEqual(retrieved_info.get_aerationtype(), value)

if __name__ == "__main__":
    unittest.main()
