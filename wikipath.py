import json, requests, pprint,os,sys,re
from minheap import MinHeap
from bs4 import BeautifulSoup
article_data = {}
known_distances = {}
years_allowed = False
stop_words = []
def main():

    if len(sys.argv) >= 2:
        start_article = sys.argv[1]
    else:
        start_article = input("Välj artikel att börja vid: ")
    if len(sys.argv) >= 3:
        stop_article = sys.argv[2]
    else:
        stop_article = input("Välj artikel att sluta vid: ")    
    if len(sys.argv) >= 4:
            if sys.argv[3] == "allow-years":
                global years_allowed
                years_allowed = True


    #pprint.pprint(json_data)

    #generate_graph(json_data)
    
    find_path_astar(start_article,stop_article)


def find_path_astar(start,stop):
    visited = []
    unvisited = [start]
    parent = {start:"None"}
    gscore = {start:0}
    #fscore = {start:1/links_in_common(start,stop)}
    fscore = MinHeap()
    fscore.insert((start,distance_heuristic(start,stop)))
    #print(fscore)
    global article_data    
    while len(unvisited) > 0:
        curr = fscore.extract()[0]
        print(ancestor_chain(parent,curr))
        if curr == stop:
            unwrap_path(parent,start,stop)
            break
        try:
            unvisited.remove(curr)
            visited.append(curr)
            
            curr_links = get_page_links(curr)["parse"]["links"]
            for l in curr_links:
                try:
                    if l["exists"] == "":
                        link = l["*"]
                        if (is_article(link)) and (link not in visited):
                            tentative_gscore = gscore[curr] + 1
                            if link not in unvisited:
                                unvisited.append(link)
                            elif tentative_gscore >= gscore[link]:
                                continue
                            
                            parent[link] = curr
                            gscore[link] = tentative_gscore
                            #fscore[link] = gscore[link] + (1/links_in_common(link,stop))
                            f = gscore[link] + distance_heuristic(link,stop)
                            fscore.insert((link,f))
                except:
                    continue
            #print(fscore.array)
            #print("{0} of {1}".format(fscore.size,fscore.capacity))
        except:
            continue
        del article_data[curr]

def distance_heuristic(link,stop):
    try:
        global known_distances
        json_file = open("known_distances.json","r")
        known_distances = json.load(json_file)
        json_file.close()
        return known_distances[link][stop]
    except:
        #print("No known distance between {0} and {1}! Please calculate in the future.".format(link,stop))
        with open("Suggestions {0}.txt".format(stop),"a+") as suggestions:
            suggestions.write(link + "\n")
        try:
            estimate_json = open("estimate_cache.json","r")
            estimate_cache = json.load(estimate_json)
            estimate_json.close()
            return estimate_cache[link][stop]
        except:
            estimate = jaccard_distance(link,stop)
            estimate_cache = {}
            with open("estimate_cache.json","r") as estimate_json:
                estimate_cache = json.load(estimate_json)
            if link in estimate_cache:
                estimate_cache[link][stop] = estimate
            else:
                estimate_cache[link] = {}
                estimate_cache[link][stop] = estimate
            with open("estimate_cache.json","w") as estimate_json:
                json.dump(estimate_cache,estimate_json)
            return estimate

def get_lowest(eligble,fscore):
    lowest_value = 10000
    lowest_key = ""
    lowest = fscore.items()
    for key,value in fscore.items():
        if value < lowest_value and key in eligble:
            lowest_value = value
            lowest_key = key
    return lowest_key

def is_article(link):
        forbidden_prefixes = ["Mall:","Portal:","Wikipedia:","Användare:","Diskussion:"]
        for i in forbidden_prefixes:
            if i in link:
                return False
        if years_allowed == False:
            match = re.findall("^\d{1,4}$",link)
            if len(match) > 0:
                return False
        return True

def links_in_common(first,second):
    first_links = get_page_links(first)["parse"]["links"]
    second_links = get_page_links(second)["parse"]["links"]
    if second in first_links:
        total = 100
    else:
        total = 0
    if len(first_links) <= len(second_links):
        shorter = first_links
        longer = second_links
    else:
        shorter = second_links
        longer = first_links
    
    for i in shorter:
        if i in longer:
            #print(i)
            total += 1
    return max(0.5,total)

def jaccard_distance(first,second):
    
    first_set = get_word_set(first)
    second_set = get_word_set(second)

    union = first_set.union(second_set)
    intersection = first_set.intersection(second_set)
 
    distance = (len(union) - len(intersection))/len(union) 
    #print("Avstånd mellan {0} och {1}: {2}".format(first,second,distance))
    return distance

def get_word_set(article):
    global stop_words
    if len(stop_words) == 0:
        json_file = open("stopwords-sv.json","r")
        stop_words = json.load(json_file)
        json_file.close()
    
    article_text = get_page_text(article)
    article_words = article_text.split(' ')
    article_nostop = [x for x in article_words if x not in stop_words]
    return set(article_nostop)

def find_path_bfs(start,stop):
    to_visit = []
    to_visit.append(start)
    visited = [start]
    parents = {start:"None"}
    while len(to_visit) > 0:
        curr = to_visit.pop(0)
        print("{0}".format(ancestor_chain(parents,curr)))
        if curr == stop:
           break
        curr_links = get_page_links(curr)["parse"]["links"]
        
        for l in curr_links:
            try:
                if l["exists"] == "":
                    link = l["*"]
                    if (not (link in visited)) and ("Mall:" not in link):
                        visited.append(link)
                        parents[link] = curr
                        to_visit.append(link)
            except:
                continue
    unwrap_path(parents,start,stop)

def ancestor_chain(parents,curr):
    chain = curr
    
    while(parents[curr] != "None"):
        curr = parents[curr]
        chain = curr + " - " + chain
    return chain 
def unwrap_path(parents,start,stop):
    path = [stop]
    curr = parents[stop]
    print(stop)
    while curr != start:
        print(curr)
        path.append(curr)
        curr = parents[curr]
    print(start)
    path.append(start)

    path.reverse()
    global known_distances
    json_file = open("known_distances.json","r")
    known_distances = json.load(json_file)
    for i in range(len(path)):
        dist = 0
        if path[i] not in known_distances:
            known_distances[path[i]] = {}
        for j in range(i,len(path)):
            if path[j] not in known_distances[path[i]]:
                known_distances[path[i]][path[j]] = dist
                dist += 1
    json_file.close()
    with open("known_distances.json","w+") as outfile:
        json.dump(known_distances,outfile)
def get_page_links(article_name):
    global article_data
    if article_name in article_data:
        return article_data[article_name] 
    filename = './cache/{0}.json'.format(article_name)
    json_data = {}
    if os.path.isfile(filename):
        json_file = open(filename)
        json_data = json.load(json_file)
        json_file.close()
        article_data[article_name] = json_data
        return json_data
    else:
        print("Downloading link data for {0}".format(article_name))
        payload = {'action':'parse','page':article_name,'format':'json','prop':'links'}
        json_data = requests.get('https://sv.wikipedia.org/w/api.php',params=payload).json()
        article_data[article_name] = json_data
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
        with open(filename,'w+') as json_file:
            json.dump(json_data,json_file)
        return json_data
def get_page_text(article_name):
    filename = './text-cache/{0}.txt'.format(article_name)
    page_text = ""

    if os.path.isfile(filename):
        page_file = open(filename)
        page_text = page_file.read()
        page_file.close()
        return page_text
    else:
        print("Downloading text for {0}".format(article_name))
        payload = {'action':'parse','page':article_name,'format':'json'}
        json_data = requests.get('https://sv.wikipedia.org/w/api.php',params=payload).json()

        html_text = json_data["parse"]["text"]["*"]

        soup = BeautifulSoup(html_text)
        page_text = ''.join(soup.findAll(text=True))

        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
        with open(filename,'w+') as page_file:
            page_file.write(page_text)
        return page_text
def generate_graph(json_data):
    title = json_data["parse"]["title"]
    links = json_data["parse"]["links"]
    
    graph_file = open("graph.gv","w+")
    graph_file.write("digraph G {\n")
    graph_file.write("\t graph [layout=dot]\n")

    for l in links:
        graph_file.write('\t"{0}" -> "{1}"\n'.format(title,l["*"]))
    graph_file.write("}")

    graph_file.close()
if __name__ == "__main__":
    main()
