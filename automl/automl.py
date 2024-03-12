import duckdb
import sklearn.model_selection
import sklearn.datasets
import sklearn.metrics
import glob
from autosklearn.regression import AutoSklearnRegressor
from autosklearn.classification import AutoSklearnClassifier


class AutoML:
    def __init__(self) -> None:
        self._table_name = "automl_data"
        self._conn = duckdb.connect()
        self._model = None
        
        self.data = None

        self.X_train = None
        self.y_train = None

        self.X_test = None
        self.y_test = None

    def _load_data(self, data_path: str) -> None:
        csv_files = glob.glob(f"{data_path}/*.csv")
        for i, csv_file in enumerate(csv_files):
            # Read each CSV file into a temporary table
            temp_table_name = f'temp_table_{i}'
            self._conn.execute(f"CREATE TABLE {temp_table_name} AS SELECT * FROM read_csv_auto('{csv_file}')")
        
            # If it's the first file, rename the temp table to the final table name
            if i == 0:
                self._conn.execute(f"ALTER TABLE {temp_table_name} RENAME TO {self._table_name}")
            else:
                # Append data from subsequent files to the combined table
                self._conn.execute(f"INSERT INTO {self._table_name} SELECT * FROM {temp_table_name}")
                self._conn.execute(f"DROP TABLE {temp_table_name}")  # Clean up the temp table

    def fit(self, data_path: str, features: list[str], label: str, is_classification: bool = True):
        self._load_data(data_path)
        X = self._conn.execute(f"SELECT {','.join(features)} FROM {self._table_name}").fetchdf()
        y = self._conn.execute(f"SELECT {label} FROM {self._table_name}").fetchdf()

        self.X_train, self.X_test, self.y_train, self.y_test = \
        sklearn.model_selection.train_test_split(X, y, random_state=1)
        self.preprocess()
        del X
        del y

        if is_classification:
            self._model = AutoSklearnClassifier(n_jobs=-1, memory_limit=None)
        else:
            self._model = AutoSklearnRegressor(
                time_left_for_this_task=120,
                per_run_time_limit=30,
                n_jobs=-1,
                memory_limit=None,
                )
        table_info = self._conn.execute(f"PRAGMA table_info('{self._table_name}')").fetchall()
        print(table_info)
        print(self.X_train.dtypes)
        self.y_train = self.y_train.reset_index()
        self._model.fit(self.X_train.astype(str), self.y_train["sellingprice"])

    def preprocess(self):
        self.X_train.fillna(999, inplace=True)
        self.y_train.fillna(999, inplace=True)

        self.X_test.fillna(999, inplace=True)
        self.y_test.fillna(999, inplace=True)

    def show_head(self, num: int = 10):
        print(self._conn.execute(f"SELECT * FROM {self._table_name} LIMIT {num}").fetch_df())

    def score(self, is_classification=False):
        y_hat = self._model.predict(self.X_test.astype(str))
        if is_classification:
            print("Accuracy score", sklearn.metrics.accuracy_score(self.y_test, y_hat))
        else:
            print("R2 score", sklearn.metrics.r2_score(self.y_test, y_hat))


if __name__ == "__main__":
    am = AutoML()
    am.fit(
        data_path="datasets/carprices/",
        features=["year","make","model","trim","body","transmission","vin","state",
                  "condition","odometer","color","interior","seller","mmr", "saledate"],
        label="sellingprice",
        is_classification=False,
        )

    am.show_head()
    am.score()