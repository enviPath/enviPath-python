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
        self.package_id = "https://envipath.org/package/57c34a2f-6310-49b1-92df-a50b5f055d6e"
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
    def test_biological_treatment_technology_additional_information(self):
        scenario_name = self.get_scenario_name()
        allowed_values = ['nitrification', 'nitrification & denitrification', 'nitrification & denitrification & biological phosphorus removal', 'nitrification & denitrification & chemical phosphorus removal', 'other']
        for value in allowed_values:
            scen = Scenario.create(self.pkg, name=scenario_name, description="to test", additional_information=[])

            info = BiologicalTreatmentTechnologyAdditionalInformation()
            info.set_biologicaltreatmenttechnology(value)

            scen.update_scenario(additional_information=[info])

            retrieved_info = scen.get_additional_information()[0]

            self.assertEqual(retrieved_info.get_biologicaltreatmenttechnology(), value)

    def test_biologicaltreatment_technology_additional_information_parser(self):
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
    def test_final_compound_concentration_additional_information(self):
        scenario_name = self.get_scenario_name()
        
        scen = Scenario.create(self.pkg, name=scenario_name, description="to test final compound concentration", additional_information=[])

        info = FinalCompoundConcentrationAdditionalInformation()
        info.set_finalcompoundconcentration(25.4)

        scen.update_scenario(additional_information=[info])

        retrieved_info = scen.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_finalcompoundconcentration(), 25.4)

    def test_final_compound_concentration_additional_information_parser(self):
        scenario_name = self.get_scenario_name()

        scen_parser = Scenario.create(self.pkg, name=scenario_name, description="to test final compound concentration parser", additional_information=[])
        data = "25.4"
        info = FinalCompoundConcentrationAdditionalInformation.parse(data)

        scen_parser.update_scenario(additional_information=[info])

        retrieved_info = scen_parser.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_finalcompoundconcentration(), 25.4)

# half-life ws
    def test_half_life_ws_additional_information_parser(self):
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
    
    def test_inoculum_source_additional_information(self):
        scenario_name = self.get_scenario_name()
        
        scen = Scenario.create(self.pkg, name=scenario_name, description="to test inoculum source", additional_information=[])

        info = InoculumSourceAdditionalInformation()
        info.set_inoculumsource("river sediment")

        scen.update_scenario(additional_information=[info])

        retrieved_info = scen.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_inoculumsource(), "river sediment")

    def test_inoculum_source_additional_information_parser(self):
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
    '''
    # oxygen content
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

    def test_partialoxygencontent_information(self):
        scenario_name = self.get_scenario_name()

        scen = Scenario.create(self.pkg, name=scenario_name, description="to test partial oxygen content information", additional_information=[])

        info = OxygenContentWaterSedimentAdditionalInformation()
        info.set_oxygen_content_water_low(5.0)
        #info.set_oxygen_content_sediment_high(6.0)

        scen.update_scenario(additional_information=[info])

        retrieved_info = scen.get_additional_information()[0]

        self.assertEqual(retrieved_info.get_oxygen_content_water_low(), 5.0)
        self.assertEqual(retrieved_info.get_oxygen_content_water_high(), 5.0)
        #self.assertEqual(retrieved_info.get_oxygen_content_sediment_low(),6.0)
        #self.assertEqual(retrieved_info.get_oxygen_content_sediment_high(), 6.0)

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
        data = "5.0 - 8.0;3.0 - 6.0"
        info = OxygenContentWaterSedimentAdditionalInformation.parse(data)

        self.assertEqual(info.get_oxygen_content_water_low(), 5.0)
        self.assertEqual(info.get_oxygen_content_water_high(), 8.0)
        self.assertEqual(info.get_oxygen_content_sediment_low(), 3.0)
        self.assertEqual(info.get_oxygen_content_sediment_high(), 6.0)

    def test_oxygencontent_information_parser_with_na(self):
        data = "NA;3.0 - 6.0"
        info = OxygenContentWaterSedimentAdditionalInformation.parse(data)

        self.assertIsNone(info.get_oxygen_content_water_low())
        self.assertIsNone(info.get_oxygen_content_water_high())
        self.assertEqual(info.get_oxygen_content_sediment_low(), 3.0)
        self.assertEqual(info.get_oxygen_content_sediment_high(), 6.0)
    '''
    # phosphorus content


    def test_phosphoruscontent_information(self):
        info = PhosphorusContentAdditionalInformation()
        influent_value = 1.5
        effluent_value = 0.5

        info.set_phosphoruscontentInfluent(influent_value)
        info.set_phosphoruscontentEffluent(effluent_value)

        self.assertEqual(info.get_phosphoruscontentInfluent(), influent_value)
        self.assertEqual(info.get_phosphoruscontentEffluent(), effluent_value)

    def test_phosphoruscontent_information_partial(self):
        info = PhosphorusContentAdditionalInformation()
        influent_value = 1.5

        info.set_phosphoruscontentInfluent(influent_value)

        self.assertEqual(info.get_phosphoruscontentInfluent(), influent_value)
        self.assertIsNone(info.get_phosphoruscontentEffluent())

    def test_phosphoruscontent_information_parser(self):
        data = "1.5;0.5"
        info = PhosphorusContentAdditionalInformation.parse(data)

        self.assertEqual(info.get_phosphoruscontentInfluent(), 1.5)
        self.assertEqual(info.get_phosphoruscontentEffluent(), 0.5)

    def test_phosphoruscontent_information_parser_single(self):
        data = "1.5;"
        info = PhosphorusContentAdditionalInformation.parse(data)

        self.assertEqual(info.get_phosphoruscontentInfluent(), 1.5)
        self.assertIsNone(info.get_phosphoruscontentEffluent())

    def test_phosphoruscontent_information_parser_na(self):
        data = ";0.5"
        info = PhosphorusContentAdditionalInformation.parse(data)

        self.assertIsNone(info.get_phosphoruscontentInfluent())
        self.assertEqual(info.get_phosphoruscontentEffluent(), 0.5)

    def test_phosphoruscontent_information_parser_na_effluent(self):
        data = "1.5;"
        info = PhosphorusContentAdditionalInformation.parse(data)

        self.assertEqual(info.get_phosphoruscontentInfluent(), 1.5)
        self.assertIsNone(info.get_phosphoruscontentEffluent())

    # purpose of wwtp
    def test_purposeofwwtp_setter_and_getter_valid(self):
        info = PurposeOfWWTPAdditionalInformation()
        valid_values = [
            "municipal ww", "industrial ww", "hospital ww", 
            "mixed ww (municipal & industrial)", "other"
        ]

        for value in valid_values:
            info.set_purposeofwwtp(value)
            self.assertEqual(info.get_purposeofwwtp(), value)

    def test_purposeofwwtp_setter_invalid(self):
        info = PurposeOfWWTPAdditionalInformation()
        invalid_values = ["residential ww", "commercial ww", "agricultural ww"]

        for value in invalid_values:
            with self.assertRaises(ValueError):
                info.set_purposeofwwtp(value)

    def test_purposeofwwtp_setter_type_error(self):
        info = PurposeOfWWTPAdditionalInformation()
        invalid_types = [123, 45.6, None, ["municipal ww"], {"purpose": "industrial ww"}]

        for value in invalid_types:
            with self.assertRaises(ValueError):
                info.set_purposeofwwtp(value)

    def test_purposeofwwtp_parser_valid(self):
        data = "municipal ww"
        info = PurposeOfWWTPAdditionalInformation.parse(data)
        self.assertEqual(info.get_purposeofwwtp(), data)

        data = "industrial ww"
        info = PurposeOfWWTPAdditionalInformation.parse(data)
        self.assertEqual(info.get_purposeofwwtp(), data)

    def test_purposeofwwtp_parser_invalid(self):
        data = "residential ww"
        with self.assertRaises(ValueError):
            PurposeOfWWTPAdditionalInformation.parse(data)

    def test_purposeofwwtp_parser_invalid_type(self):
        data = 12345
        with self.assertRaises(ValueError):
            PurposeOfWWTPAdditionalInformation.parse(data)

    # rate constant

    def test_setter_and_getter_valid(self):
        info = RateConstantAdditionalInformation()

        # Valid values
        valid_lower = 0.1
        valid_upper = 0.5
        valid_order = "first order"
        valid_corrected = "sorption corrected"
        #valid_comment = "Test comment"

        info.set_rateconstantlower(valid_lower)
        info.set_rateconstantupper(valid_upper)
        info.set_rateconstantorder(valid_order)
        info.set_rateconstantcorrected(valid_corrected)
        #info.set_rateconstantcomment(valid_comment)

        self.assertEqual(info.get_rateconstantlower(), valid_lower)
        self.assertEqual(info.get_rateconstantupper(), valid_upper)
        self.assertEqual(info.get_rateconstantorder(), valid_order)
        self.assertEqual(info.get_rateconstantcorrected(), valid_corrected)
        self.assertIsNone(info.get_rateconstantcomment())

    def test_setter_invalid(self):
        info = RateConstantAdditionalInformation()

        # Invalid values
        invalid_lower = "abc"
        invalid_upper = "def"
        invalid_order = "third order"
        invalid_corrected = "sorption and biodegradation corrected"
        invalid_comment = 12345

        with self.assertRaises(ValueError):
            info.set_rateconstantlower(invalid_lower)

        with self.assertRaises(ValueError):
            info.set_rateconstantupper(invalid_upper)

        with self.assertRaises(ValueError):
            info.set_rateconstantorder(invalid_order)

        with self.assertRaises(ValueError):
            info.set_rateconstantcorrected(invalid_corrected)


    def test_parser_valid(self):
        data_string = "first order;sorption corrected;0.1 - 0.5;Test comment"
        info = RateConstantAdditionalInformation.parse(data_string)

        self.assertEqual(info.get_rateconstantorder(), "first order")
        self.assertEqual(info.get_rateconstantcorrected(), "sorption corrected")
        self.assertEqual(info.get_rateconstantlower(), 0.1)
        self.assertEqual(info.get_rateconstantupper(), 0.5)
        self.assertEqual(info.get_rateconstantcomment(), "Test comment")

    def test_parser_valid_no_comment(self):
        data_string = "second order;sorption corrected;0.1 - 0.5;no comment"
        info = RateConstantAdditionalInformation.parse(data_string)

        self.assertEqual(info.get_rateconstantorder(), "second order")
        self.assertEqual(info.get_rateconstantcorrected(), "sorption corrected")
        self.assertEqual(info.get_rateconstantlower(), 0.1)
        self.assertEqual(info.get_rateconstantupper(), 0.5)
        self.assertEqual(info.get_rateconstantcomment(),"no comment")

    def test_parser_malformed_data(self):
        data_string = "first order;sorption corrected;0.1 - 0.5;Test comment"
        info = RateConstantAdditionalInformation.parse(data_string)

        self.assertEqual(info.get_rateconstantorder(), "first order")
        self.assertEqual(info.get_rateconstantcorrected(), "sorption corrected")
        self.assertEqual(info.get_rateconstantlower(), 0.1)
        self.assertEqual(info.get_rateconstantupper(), 0.5)
        self.assertEqual(info.get_rateconstantcomment(), "Test comment")


    # redox 
    def test_setter_and_getter_valid(self):
        info = RedoxAdditionalInformation()

        # Valid redox types
        valid_types = ['aerob', 'anaerob', 'anaerob: iron-reducing', 'anaerob: sulfate-reducing',
                       'anaerob: methanogenic conditions', 'oxic', 'nitrate-reducing']

        for redox_type in valid_types:
            info.set_redoxType(redox_type)
            self.assertEqual(info.get_redoxType(), redox_type)

    def test_setter_invalid(self):
        info = RedoxAdditionalInformation()

        # Invalid redox types
        invalid_types = ['oxidative', 'anaerobic: sulfur-reducing', 'oxic: high oxygen']

        for redox_type in invalid_types:
            with self.assertRaises(ValueError):
                info.set_redoxType(redox_type)

    def test_parser_valid(self):
        data_string = "aerob"
        info = RedoxAdditionalInformation.parse(data_string)
        self.assertEqual(info.get_redoxType(), "aerob")

    def test_parser_invalid(self):
        # Test parsing with invalid data
        with self.assertRaises(ValueError):
            RedoxAdditionalInformation.parse("invalid_redox_type")


    # redox potential

    def test_setter_and_getter_valid(self):
        info = RedoxPotentialAdditionalInformation()
        info.set_lowPotentialWater(100.0)
        info.set_highPotentialWater(200.0)
        info.set_lowPotentialSediment(-50.0)
        info.set_highPotentialSediment(10.0)

        self.assertEqual(info.get_lowPotentialWater(), 100.0)
        self.assertEqual(info.get_highPotentialWater(), 200.0)
        self.assertEqual(info.get_lowPotentialSediment(), -50.0)
        self.assertEqual(info.get_highPotentialSediment(), 10.0)

    def test_parser_with_valid_data(self):
        data = "100.0 - 200.0;-50.0 - 10.0"
        info = RedoxPotentialAdditionalInformation.parse(data)

        self.assertEqual(info.get_lowPotentialWater(), 100.0)
        self.assertEqual(info.get_highPotentialWater(), 200.0)
        self.assertEqual(info.get_lowPotentialSediment(), -50.0)
        self.assertEqual(info.get_highPotentialSediment(), 10.0)

    def test_parser_with_NA(self):
        data = "NA;NA"
        info = RedoxPotentialAdditionalInformation.parse(data)

        self.assertIsNone(info.get_lowPotentialWater())
        self.assertIsNone(info.get_highPotentialWater())
        self.assertIsNone(info.get_lowPotentialSediment())
        self.assertIsNone(info.get_highPotentialSediment())

    # reference 

    def test_setter_and_getter(self):
        info = ReferenceAdditionalInformation()
        info.set_reference("PMID:12345678")

        self.assertEqual(info.get_reference(), "PMID:12345678")

    def test_parser_with_valid_data(self):
        data = "PMID:12345678"
        info = ReferenceAdditionalInformation.parse(data)

        self.assertEqual(info.get_reference(), "PMID:12345678")

    # sampling depth
    def test_setter_and_getter(self):
        info = SamplingDepthAdditionalInformation()
        info.set_samplingDepthMin(10.0)
        info.set_samplingDepthMax(20.0)

        self.assertEqual(info.get_samplingDepthMin(), 10.0)
        self.assertEqual(info.get_samplingDepthMax(), 20.0)

    def test_parser_with_single_depth(self):
        data = "15.0"
        info = SamplingDepthAdditionalInformation.parse(data)

        self.assertEqual(info.get_samplingDepthMin(), 15.0)
        self.assertEqual(info.get_samplingDepthMax(), 15.0)

    def test_parser_with_range(self):
        data = "10.0;20.0"
        info = SamplingDepthAdditionalInformation.parse(data)

        self.assertEqual(info.get_samplingDepthMin(), 10.0)
        self.assertEqual(info.get_samplingDepthMax(), 20.0)

    # sediment porosity

    def test_setter_and_getter(self):
        info = SedimentPorosityAdditionalInformation()
        info.set_sedimentporosity(0.4)

        self.assertEqual(info.get_sedimentporosity(), 0.4)

    def test_parser(self):
        data = "0.35"
        info = SedimentPorosityAdditionalInformation.parse(data)

        self.assertNotEqual(info.get_sedimentporosity(), 0.35)

    # sludge retention time
    def test_setter_and_getter(self):
        info = SludgeRetentionTimeAdditionalInformation()
        info.set_sludgeretentiontimeType('sludge age')
        info.set_sludgeretentiontime(20.5)

        self.assertEqual(info.get_sludgeretentiontimeType(), 'sludge age')
        self.assertEqual(info.get_sludgeretentiontime(), 20.5)

    def test_parser(self):
        data = "sludge retention time;25.0"
        info = SludgeRetentionTimeAdditionalInformation.parse(data)

        self.assertEqual(info.get_sludgeretentiontimeType(), 'sludge retention time')
        self.assertEqual(info.get_sludgeretentiontime(), 25.0)

    # soil classification system
    def test_setter_and_getter(self):
        info = SoilClassificationAdditionalInformation()
        info.set_soilclassificationsystem('USDA')

        self.assertEqual(info.get_soilclassificationsystem(), 'USDA')

    def test_parser(self):
        data = "UK"
        info = SoilClassificationAdditionalInformation.parse(data)

        self.assertEqual(info.get_soilclassificationsystem(), 'UK')

    # soil source


    def test_setter_and_getter(self):
        info = SoilSourceAdditionalInformation()
        info.set_soilsourcedata('Sample Location A')

        self.assertEqual(info.get_soilsourcedata(), 'Sample Location A')

    def test_parser(self):
        data = "Sample Location B"
        info = SoilSourceAdditionalInformation.parse(data)

        self.assertEqual(info.get_soilsourcedata(), 'Sample Location B')

    # soil texture type
    
    def test_setter_and_getter(self):
        info = SoilTexture1AdditionalInformation()
        info.set_soilTextureType("CLAY")

        self.assertEqual(info.get_soilTextureType(), "CLAY")

    def test_setter_invalid_value(self):
        info = SoilTexture1AdditionalInformation()
        with self.assertRaises(ValueError) as context:
            info.set_soilTextureType("INVALID_TEXTURE")
        self.assertTrue("INVALID_TEXTURE is not an allowed soilTextureType" in str(context.exception))

    def test_parser(self):
        data = "SANDY_LOAM"
        info = SoilTexture1AdditionalInformation.parse(data)

        self.assertEqual(info.get_soilTextureType(), "SANDY_LOAM")

    def test_parser_invalid_value(self):
        data = "INVALID_TEXTURE"
        with self.assertRaises(ValueError) as context:
            SoilTexture1AdditionalInformation.parse(data)
        self.assertTrue("INVALID_TEXTURE is not an allowed soilTextureType" in str(context.exception))

    # soil texture 2

    def test_setter_and_getter(self):
        data = {
            "sand": 45.0,
            "silt": 34.0,
            "clay": 21.0
        }
        soil_texture = SoilTexture2AdditionalInformation(**data)
        self.assertEqual(soil_texture.get_sand(), 45.0)
        self.assertEqual(soil_texture.get_silt(), 34.0)
        self.assertEqual(soil_texture.get_clay(), 21.0)

    def test_parser(self):
        data_string = "Soil texture 2: 45.0% sand; 34.0% silt; 21.0% clay"
        soil_texture = SoilTexture2AdditionalInformation.parse(data_string)
        self.assertEqual(soil_texture.get_sand(), 45.0)
        self.assertEqual(soil_texture.get_silt(), 34.0)
        self.assertEqual(soil_texture.get_clay(), 21.0)

    def test_parser_with_whitespace(self):
        data_string = "Soil texture 2:  45.0% sand; 34.0% silt; 21.0% clay  "
        soil_texture = SoilTexture2AdditionalInformation.parse(data_string)
        self.assertEqual(soil_texture.get_sand(), 45.0)
        self.assertEqual(soil_texture.get_silt(), 34.0)
        self.assertEqual(soil_texture.get_clay(), 21.0)

    def test_parser_with_different_order(self):
        data_string = "Soil texture 2: 34.0% silt; 21.0% clay; 45.0% sand"
        soil_texture = SoilTexture2AdditionalInformation.parse(data_string)
        self.assertNotEqual(soil_texture.get_sand(), 45.0)
        self.assertNotEqual(soil_texture.get_silt(), 34.0)
        self.assertNotEqual(soil_texture.get_clay(), 21.0)


    # solvent compound solution

    def test_setter_and_getter(self):
        info = SolventForCompoundSolutionAdditionalInformation()
        info.set_solventforcompoundsolution1(50.0)
        info.set_solventforcompoundsolution2(30.0)
        info.set_solventforcompoundsolution3(20.0)

        self.assertEqual(info.get_solventforcompoundsolution1(), 50.0)
        self.assertEqual(info.get_solventforcompoundsolution2(), 30.0)
        self.assertEqual(info.get_solventforcompoundsolution3(), 20.0)

    def test_parser(self):
        data = "50.0;30.0;20.0"
        info = SolventForCompoundSolutionAdditionalInformation.parse(data)

        self.assertEqual(info.get_solventforcompoundsolution1(), 50.0)
        self.assertEqual(info.get_solventforcompoundsolution2(), 30.0)
        self.assertEqual(info.get_solventforcompoundsolution3(), 20.0)




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

        # Update scenario with the additional information
        scen_parser.update_scenario(additional_information=[dissolved_oxygen_info])

        # Retrieve the additional information from the scenario
        retrieved_info = scen_parser.get_additional_information()[0]

        # Verify the values for DissolvedOxygenConcentrationAdditionalInformation
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
        # Test DissolvedOxygenConcentrationAdditionalInformation
        data = "2.0;8.0"
        info = OxygenUptakeRateAdditionalInformation.parse(data)

        # Update scenario with the additional information
        scen_parser.update_scenario(info)

        # Retrieve the additional information from the scenario
        retrieved_info = scen_parser.get_additional_information()[0]

        # Verify the values for DissolvedOxygenConcentrationAdditionalInformation
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
