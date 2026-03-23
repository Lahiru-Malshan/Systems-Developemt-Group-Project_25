# Elena Ho - 25044389
# logic/search.py

class SearchEngine:
    @staticmethod
    def apply_logic(data_list, search_term="", filters=None):
        data = list(data_list)

        if search_term:
            search_term = search_term.lower()
            data = [
                item for item in data
                if any(search_term in str(val).lower() for val in item.values())
            ]

        if filters:
            for key, value in filters.items():
                if value and not str(value).startswith("All"):
                    data = [t for t in data if t.get(key) == value]
        return data