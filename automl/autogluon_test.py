from autogluon.tabular import TabularPredictor

predictor = TabularPredictor(label="price").fit("../error_data.csv")
predictions = predictor.predict("../error_data.csv")
