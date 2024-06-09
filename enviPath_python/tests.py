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
