import requests
import json
import random


class HistoryFetcher:
    def __init__(self) -> None:
        self.baseurl = "https://en.wikipedia.org/api/rest_v1/feed/onthisday"
        self.limit = 5
        self.keywords = [
            "Ethiopia",
            "Addis Ababa",
            "Haile Selassie",
            "Axum",
            "Lalibela",
            "Menelik II",
            "Tewodros II",
            "Gondar",
            "Adwa",
            "Derg",
            "Amharic",
            "Ge’ez",
            "Lucy",
            "Simien Mountains",
            "Blue Nile",
            "Lake Tana",
            "Meskel",
            "Timkat",
        ]

    def fetch_by_category(self, category, month, day):
        url = f"{self.baseurl}/{category}/{month}/{day}"

        response = requests.get(url)
        if response.status_code != 200:
            return []

        return response.json().get(category)

    def filter_items(self, items):
        filtered = []

        for item in items:
            text = item.get("text", "")
            link = (
                item.get("pages", [{}])[0]
                .get("content_urls", {})
                .get("desktop", {})
                .get("page", "")
            )
            year = item.get("year", "?")

            if any(j.lower() in text.lower() for j in self.keywords):
                filtered.append(f"📅 {year} - {text}\n 🔗 {link}")
        return filtered

    def fill_random(self, items, filtered):
        remaning = self.limit - len(filtered)

        if remaning <= 0:
            return filtered[: self.limit]

        pool = [
            f"📅 {item.get('year','?')} - {item.get('text','')}\n 🔗 {item.get("pages", [{}])[0]\
                .get("content_urls", {})\
                .get("desktop", {})\
                .get("page", "")}"
            for item in items
            if f"📅 {item.get('year','?')} - {item.get('text','')}" not in filtered
        ]

        filtered += random.sample(pool, remaning)

        return filtered[: self.limit]

    def summary(self, month, day):
        result = {}
        for category in ["events", "deaths", "births"]:
            items = self.fetch_by_category(category, month, day)
            filtered = self.filter_items(items)
            full_list = self.fill_random(items, filtered)
            result[category] = full_list

        return result

