from dataclasses import dataclass

@dataclass
class TravelEmissions:
    # Facteurs génériques par défaut (gCO2/km)
    default_factors = {
        "car": {"construction": 40, "fuel": 120, "infra": 0.7, "passager_supp": 0.04},
        "bus": {"construction": 20, "fuel": 80, "infra": 0.5},
        "train": { "infra": 6.5},
        "bike": {"construction": 5, "fuel_humain": 16},
        "plane": {"amont": 50, "combustion": 250, "construction": 30, "infra": 0.3, "hoc_multiplier": 1.7, "holding": 3810},
        "ferry": {"combustion": 200, "services": 110, "construction": 20},
        "sailboat": {"combustion": 50},
    }

    train_amont_factors = {
        "FR": (2.3 + 5.8 + 22.9 + 6.6 + 9.4) / 5,  # France
        "IT": 31.7,  # Italie
        "DE": 66.8,  # Allemagne
        "ES": 51.4,  # Espagne
        "AT": 23.5,  # Autriche
        "SE": 12.9,  # Suède
        "BE": 48.4,  # Belgique
        "CH": 3.74,  # Suisse
        "FI": 45.2,  # Finlande
        "GR": 66.2,  # Grèce
        "IE": 38.8,  # Irlande
        "NO": 40,    # Norvège
        "PT": 61.5,  # Portugal
        "LU": 39.7,  # Luxembourg
        "GB": 31,    # Grande-Bretagne
        "DK": (6 + 32 / 2),  # Danemark
        "NL": (24 + 26) / 2, # Pays-Bas
        "CN": 18,    # Chine
        "JP": 23,    # Japon
        "US": 90,    # USA
        "IN": 8,     # Inde
        "RU": 26,    # Russie
        "PL": 25,    # Pologne
        "HU": 25,    # Hongrie
        "RO": 25,    # Roumanie
        "BG": 25,    # Bulgarie
        "CZ": 25,    # Tchéquie
        "EE": 25,    # Estonie
        "LV": 25,    # Lettonie
        "LT": 25,    # Lituanie
        "SK": 25,    # Slovaquie
        "SI": 25,    # Slovénie
        "Autre": 88.39,
    }

    # Facteurs fabrication par pays et type de train (gCO2 eq / personne / km)
    train_fabrication_factors = {
        "FR": (0.63 + 1.7 + 4.79 + 3.18 + 2.6) / 5,
        "Autre": 0.63,
    }

    def car(self, distance_km: float, passengers: int = 1) -> float:
        f = self.default_factors['car']
        total = (
            distance_km * f['construction'] +
            distance_km * f['fuel'] +
            distance_km * f['infra'] +
            distance_km * f['fuel'] * f['passager_supp'] * max(0, passengers - 1)
        )
        return total / 1000  # kgCO2eq

    def bus(self, distance_km: float) -> float:
        f = self.default_factors['bus']
        total = distance_km * (f['construction'] + f['fuel'] + f['infra'])
        return total / 1000

    def train(self, segments: list, passengers: int = 1) -> float:
        total_distance = sum(dist for dist, _ in segments)
        infra_total = total_distance * self.default_factors['train']['infra']
        amont_total = sum(dist * (self.train_amont_factors[country] if country in self.train_amont_factors else self.train_amont_factors['Autre']) for dist, country in segments)
        fab_total = sum(dist * (self.train_fabrication_factors[country] if country in self.train_fabrication_factors else self.train_fabrication_factors['Autre']) for dist, country in segments)
        return (infra_total + amont_total + fab_total) / passengers / 1000

    def bike(self, distance_km: float) -> float:
        f = self.default_factors['bike']
        total = distance_km * (f['construction'] + f['fuel_humain'])
        return total / 1000

    def sailboat(self, distance_km: float) -> float:
        f = self.default_factors['sailboat']
        total = distance_km * f['combustion']
        return total / 1000

    def ferry(self, distance_km: float, use_cabin: bool = True) -> float:
        f = self.default_factors['ferry']
        services = f['services'] if use_cabin else 0
        total = distance_km * (f['combustion'] + services + f['construction'])
        return total / 1000

    def plane(self, distance_km: float) -> float:
        f = self.default_factors['plane']
        d_detour = distance_km  # ici on peut appliquer un coef detour si nécessaire
        total = (
            d_detour * f['amont'] +
            d_detour * f['combustion'] +
            d_detour * f['construction'] +
            d_detour * f['infra'] +
            d_detour * f['combustion'] * f['hoc_multiplier'] +
            f['holding']
        )
        return total / 1000

    def total_emissions(self, trips: list) -> float:
        total = 0
        for trip in trips:
            mode = trip['mode']
            if mode == 'car':
                total += self.car(trip['distance_km'], trip.get('passengers', 1))
            elif mode == 'bus':
                total += self.bus(trip['distance_km'])
            elif mode == 'train':
                total += self.train(trip['segments'], trip.get('passengers', 1))
            elif mode == 'bike':
                total += self.bike(trip['distance_km'])
            elif mode == 'ferry':
                total += self.ferry(trip['distance_km'], trip.get('use_cabin', True))
            elif mode == 'sailboat':
                total += self.sailboat(trip['distance_km'])
            elif mode == 'plane':
                total += self.plane(trip['distance_km'])
        return total

# Exemple d'utilisation
if __name__ == "__main__":
    emissions_calculator = TravelEmissions()
    trips = [
        {"mode": "car", "distance_km": 100, "passengers": 2},
        {"mode": "train", "segments": [(200, "FR"), (150, "DE")], "passengers": 1},
        {"mode": "plane", "distance_km": 1000},
    ]
    total_emissions = emissions_calculator.total_emissions(trips)
    print(f"Total CO2 emissions for the trips: {total_emissions:.2f} kgCO2eq")

    train_only = emissions_calculator.train([(300, "FR"), (200, "IT")], passengers=1)
    print(f"Total CO2 emissions for the train trip: {train_only:.2f} kgCO2eq")