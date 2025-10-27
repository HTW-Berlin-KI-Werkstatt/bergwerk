import requests
from tools import tools
from datetime import datetime
from json import loads

config = tools.Config()

HOST = "http://api/wiki/menuinput/"
languages = loads(config.get_value("languages")).keys()


def get_node(menuinput, language):
    try:
        payload = {"menuinput": menuinput, "language": language, "uid": "cron"}
        response = requests.post(HOST, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        print(f"Error processing page {menuinput}: {e}")
        return None

def build_tree(menuinput, parent=None, visited=None, missing_nodes=None, nodes_without_category_content=None, language=None):
    try:
        if visited is None:
            visited = set()
        if missing_nodes is None:
            missing_nodes = {}
        if nodes_without_category_content is None:
            nodes_without_category_content = set()

        if menuinput in visited:
            return
        visited.add(menuinput)

        node = get_node(menuinput, language)
        if node is None:
            parent_display = parent if parent is not None else 'Root'
            if menuinput not in missing_nodes:
                missing_nodes[menuinput] = set()
            missing_nodes[menuinput].add(parent_display)
            print(f"Node '{menuinput}' is missing. Referenced by '{parent_display}'")
            return

        if not "[[Category:Content]]" in tools.get_entire_page(menuinput):
            nodes_without_category_content.add(menuinput)
            print(f"Node '{menuinput}' has no [[Category:Content]].")

        menuitems = node.get('menuitems', [])
        for item in menuitems:
            link = item.get('link')
            if link:
                build_tree(link, menuinput, visited, missing_nodes, nodes_without_category_content, language=language)

        return visited, missing_nodes, nodes_without_category_content
    
    except Exception as e:
        print(f"Error processing page {menuinput}: {e}")
        return visited, missing_nodes, nodes_without_category_content

if __name__ == '__main__':

    print("Running check content cron!")

    now = datetime.now()
    check_time = now.strftime("%A, %B %d, %Y %I:%M %p")
    check_content_page = f"= Last check: {check_time} =\n"


    for l in languages:

        check_content_page += f"== Content check for language {l} ==\n"

        try:
            visited_nodes, missing_nodes, nodes_without_category_content = build_tree('Start', language=l)

            check_content_page += f"Visited pages: "
            for n in visited_nodes:
                check_content_page += f"[[{n}|{n}]] - "
            
            check_content_page += "\n\n"

            if missing_nodes:
                for missing_node, parents in missing_nodes.items():
                    parent_list = ', '.join(parents)
                    check_content_page += f"Page [[{missing_node}|{missing_node}]] is missing. Referenced by: {parent_list}\n\n"
            if nodes_without_category_content:
                check_content_page += f"Pages without Category Content: "
                for p in nodes_without_category_content:
                    check_content_page += f"[[{p}|{p}]] - "
                check_content_page += "\n\n"
        except Exception as e:
            check_content_page += f"Error processing page 'Start': {e}\n\n"

        tools.create_or_update_page("Check_content", check_content_page)
