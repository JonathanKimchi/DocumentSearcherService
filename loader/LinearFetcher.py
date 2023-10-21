import requests

class LinearFetcher:
    LINEAR_API_URL = "https://api.linear.app/graphql"

    @staticmethod
    def fetch_all_issues(api_token):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_token}"
        }
        
        query = """
        query {
            issues {
                nodes {
                    id
                    title
                    description
                }
            }
        }
        """
        
        response = requests.post(LinearFetcher.LINEAR_API_URL, headers=headers, json={"query": query})
        if response.status_code == 200:
            return response.json()["data"]["issues"]["nodes"]
        else:
            return []

    @staticmethod
    def convert_issues_to_text(issues):
        text = ""
        for issue in issues:
            text += f"Issue ID: {issue['id']}\n"
            text += f"Title: {issue['title']}\n"
            text += f"Description: {issue['description']}\n\n"
        return text

    @classmethod
    def fetch_and_convert_issues(cls, api_token):
        issues = cls.fetch_all_issues(api_token)
        return cls.convert_issues_to_text(issues)
