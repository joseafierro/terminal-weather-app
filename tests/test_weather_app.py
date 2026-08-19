import unittest

import weather_app


class WeatherAppTests(unittest.TestCase):
    def test_version(self):
        self.assertEqual(weather_app.__version__, "1.0.0")

    def test_compass_direction_cardinal_points(self):
        self.assertEqual(weather_app.compass_direction(0), "N")
        self.assertEqual(weather_app.compass_direction(90), "E")
        self.assertEqual(weather_app.compass_direction(180), "S")
        self.assertEqual(weather_app.compass_direction(270), "W")
        self.assertEqual(weather_app.compass_direction(360), "N")

    def test_location_label_uses_available_fields(self):
        place = {
            "name": "Ciudad Juarez",
            "admin1": "Chihuahua",
            "country": "Mexico",
        }
        self.assertEqual(
            weather_app.location_label(place),
            "Ciudad Juarez, Chihuahua, Mexico",
        )

    def test_location_label_skips_missing_fields(self):
        self.assertEqual(
            weather_app.location_label({"name": "GPS coordinates"}),
            "GPS coordinates",
        )


if __name__ == "__main__":
    unittest.main()
