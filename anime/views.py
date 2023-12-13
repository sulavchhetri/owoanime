from django.shortcuts import render
from bs4 import BeautifulSoup
from curl_cffi import requests
from django.shortcuts import redirect
from viewscounter.models import ViewsCounter as vc
from viewscounter.models import CategoryView as cv
from viewscounter.models import EpisodeView as ev
try:
    from custom.meta import meta
except:
    pass

def increaseview(name):
    try:
        page = vc.objects.get(page=name)
        page.views += 1
        page.save()
    except:
        page = vc(page=name, views=1)
        page.save()

def categoryview(name):
    try:
        page = cv.objects.get(title=name)
        page.views += 1
        page.save()
    except:
        page = cv(title=name, views=1)
        page.save()

def episodeview(name):
    try:
        page = ev.objects.get(episode=name)
        page.views += 1
        page.save()
    except:
        page = ev(episode=name, views=1)
        page.save()

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'en-GB,en;q=0.5',
    'Referer':'https://google.com',
    'DNT':'1'
}

def getseason(site):
    season = site.find('nav', class_='menu_series cron').find_all('li')
    season_data = list()
    for s in season:
        sdata = {}
        sdata['year'] = s.span.text
        links = []
        for l in s.find_all('a'):
            link = [l['href'], l.text]
            links.append(link)
        sdata['links'] = links
        season_data.append(sdata)
    return season_data

def getrecent(site):
    recrel = site.find('nav', class_='menu_recent').find_all('li')[0:10]
    recrel_data = [{'image':"https://ww4.gogoanime2.org"+r.a.div['style'][16:-2], 'name':r.a.text.strip(), 'link':'/episode'+r.a['href'], 'episode':r.p.text} for r in recrel]
    return recrel_data

def home(request):
    try:
        metadescription = meta['home']
    except:
        metadescription = ''
    pagetitle = 'Home'
    increaseview(pagetitle)
    url = 'https://ww4.gogoanime2.org/home'
    response = requests.get(url, headers=headers,
                           impersonate='chrome110', timeout=20).text
    site = BeautifulSoup(response, 'html.parser')
    #OnGoing Series
    ongoing = site.find_all('nav', class_='menu_series cron')[0].find_all('li')[0:20]
    ongoing_data = [{'link':a.a['href'], 'name':a.a.text.strip(), 'image': 'https://ww4.gogoanime2.org/images/225_318/'+a.a['href'].split('/')[-1]+'.jpg', 'sub':a.a.text.strip()[-4:-1]} for a in ongoing[0:20]]

    #Recent Release
    r_release = site.find('div', class_='last_episodes loaddub recentloader').find_all('li')

    r_data = [{'name':r.p.a.text, 'image':'https://ww4.gogoanime2.org'+r.div.a.img['src'], 'link':'/episode'+r.div.a['href'].split('watch')[1], 'episode':r.find_all('p')[1].text}  for r in r_release]

    #Season
    season = site.find_all('nav', class_='menu_series cron')[1].find_all('li')
    season_data = list()
    for s in season:
        sdata = {}
        sdata['year'] = s.span.text
        links = []
        for l in s.find_all('a'):
            link = [l['href'], l.text]
            links.append(link)
        sdata['links'] = links
        season_data.append(sdata)

    #Genres
    genres = site.find('nav', class_='menu_series genre right').find_all('li')
    col1 = []
    col2 = []
    for i in range(0,len(genres),2):
        gen = {}
        gen['name'] = genres[i].a.text
        gen['link'] = genres[i].a['href']
        col1.append(gen)
        try:
            gen = {}
            gen['name'] = genres[i+1].a.text
            gen['link'] = genres[i+1].a['href']
            col2.append(gen)
        except:
            pass
    genres = [col1,col2]

    #Popular Ongoing Update
    url = 'https://ajax.gogo-load.com/ajax/page-recent-release-ongoing.html?page=1'
    response = requests.get(url, headers=headers,
                           impersonate='chrome110', timeout=20).text
    site = BeautifulSoup(response, 'html.parser')
    day = site.find('div', class_='added_series_body popular').find_all('li')
    day_data = []
    for d in day:
        day_dict = {}
        day_dict['name'] = d.find_all('a')[1].text.strip()
        day_dict['image'] = d.a.div['style'][17:-3]
        day_dict['episode'] = d.find_all('p')[1].a.text
        day_dict['link'] = d.a['href']
        genre=[]
        for g in d.p.find_all('a'):
            genre.append(g.text)
        day_dict['genre'] = genre
        day_data.append(day_dict)
    return render(request, 'home.html', {'lrel':r_data, 'popog':day_data, 'season':season_data, 'ongoing': ongoing_data, 'genres':genres, 'activetab':'home', 'pagetitle':pagetitle, 'metadescription':metadescription})

def newSeason(request):
    pagetitle = 'NewSeason'
    increaseview(pagetitle)
    try:
        pageno = request.GET['page']
    except:
        pageno = ''
    url = 'https://gogoanime.pe/new-season.html'+'?page='+pageno
    response = requests.get(url, headers=headers,
                           impersonate='chrome110', timeout=20).text
    site = BeautifulSoup(response, 'html.parser')

    #New Season
    news = site.find('div', class_='last_episodes').find_all('li')
    news_data = [{'name':r.p.a.text, 'image':r.div.a.img['src'], 'link':r.div.a['href'], 'episode':r.find_all('p')[1].text.strip(), 'sub':r.p.a.text.strip()[-4:-1]}  for r in news]
    page = site.find('ul', class_='pagination-list').find_all('li')
    pages = [{'link':p.a['href'], 'number':p.a.text} for p in page]
    if pageno == '':
        pageno = '1'

    #Recent Release
    recrel_data = getrecent(site)

    #Season
    season_data = getseason(site)

    return render(request, 'newseason.html', {'season':season_data, 'lrel':news_data, 'popog':recrel_data, 'pages':pages, 'activepage':pageno, 'activetab':'newseason', 'pagetitle':pagetitle})


def popular(request):
    pagetitle = 'Popular'
    increaseview(pagetitle)
    try:
        pageno = request.GET['page']
    except:
        pageno = ''
    url = 'https://gogoanime.pe/popular.html'+'?page='+pageno
    response = requests.get(url, headers=headers,
                           impersonate='chrome110', timeout=20).text
    site = BeautifulSoup(response, 'html.parser')

    #New Season
    news = site.find('div', class_='last_episodes').find_all('li')
    news_data = [{'name':r.p.a.text, 'image':r.div.a.img['src'], 'link':r.div.a['href'], 'episode':r.find_all('p')[1].text.strip(), 'sub':r.p.a.text.strip()[-4:-1]}  for r in news]
    page = site.find('ul', class_='pagination-list').find_all('li')
    pages = [{'link':p.a['href'], 'number':p.a.text} for p in page]
    if pageno == '':
        pageno = '1'

    #Recent Release
    recrel_data = getrecent(site)
    #Season
    season_data = getseason(site)

    return render(request, 'popular.html', {'season':season_data, 'lrel':news_data, 'popog':recrel_data, 'pages':pages, 'activepage':pageno, 'activetab':'popular', 'pagetitle':pagetitle})


def movies(request):
    pagetitle = 'Movies'
    increaseview(pagetitle)
    try:
        pageno = request.GET['page']
    except:
        pageno = ''
    try:
        aph = request.GET['aph']
    except:
        aph = ''
    url = 'https://gogoanime.pe/anime-movies.html'+'?aph='+aph+'&page='+pageno
    response = requests.get(url, headers=headers,
                           impersonate='chrome110', timeout=20).text
    site = BeautifulSoup(response, 'html.parser')

    #Anime Movies
    news = site.find('div', class_='last_episodes').find_all('li')
    news_data = [{'name':r.p.a.text, 'image':r.div.a.img['src'], 'link':r.div.a['href'], 'episode':r.find_all('p')[1].text.strip(), 'sub':r.p.a.text.strip()[-4:-1]}  for r in news]
    try:
        page = site.find('ul', class_='pagination-list').find_all('li')
        pages = [{'link':p.a['href'], 'number':p.a.text} for p in page]
        if pageno == '':
            pageno = '1'
    except:
        pages = ''
        pageno = 'null'
    ap = site.find('div', class_='list_search').find_all('li')
    aphs = [{'link':p.a['href'][18:], 'aph':p.a.text} for p in ap]
    if aph == '':
        aph = 'All'

    #Recent Release
    recrel_data = getrecent(site)

    #Season
    season_data = getseason(site)

    return render(request, 'movies.html', {'season':season_data, 'lrel':news_data, 'popog':recrel_data, 'pages':pages, 'activepage':pageno, 'aphs':aphs, 'activeaph':aph, 'activetab':'movies', 'pagetitle':pagetitle})

def animeList(request):
    pagetitle = 'AnimeList'
    increaseview(pagetitle)
    try:
        pageno = request.GET['page']
    except:
        pageno = ''
    try:
        aph = request.GET['aph']
    except:
        aph = ''
    if aph == '' or aph == 'All':
        url = 'https://gogoanime.pe/anime-list.html'+'?page='+pageno
    else:
        url = 'https://gogoanime.pe/anime-list-'+aph+'?page='+pageno
        if aph == '0':
            aph = '#'
    response = requests.get(url, headers=headers,
                           impersonate='chrome110', timeout=20).text
    site = BeautifulSoup(response, 'html.parser')

    #Anime List
    news = site.find('ul', class_='listing').find_all('li')
    news_data = [{'name':r.a.text, 'image':r['title'].split('"')[3], 'link':r.a['href'], 'episode':''.join(r['title'].split('<span>')[2].split('</p>')[0].split('</span>')), 'sub':r.a.text.strip()[-4:-1]}  for r in news]
    try:
        page = site.find('ul', class_='pagination-list').find_all('li')
        pages = [{'link':p.a['href'][1:], 'number':p.a.text} for p in page]
        if pageno == '':
            pageno = '1'
    except:
        pages = ''
        pageno = 'null'
    ap = site.find('div', class_='list_search').find_all('li')
    aphs = [{'link':'?aph='+p.a.text, 'aph':p.a.text} for p in ap]
    if aph == '':
        aph = 'All'

    #Recent Release
    recrel_data = getrecent(site)

    #Season
    season_data = getseason(site)

    return render(request, 'animelist.html', {'season':season_data, 'lrel':news_data, 'popog':recrel_data, 'pages':pages, 'activepage':pageno, 'aphs':aphs, 'activeaph':aph, 'activetab':'anime', 'pagetitle':pagetitle})

def search(request):
    pagetitle = 'Search Results'
    increaseview(pagetitle)
    try:
        pageno = request.GET['page']
    except:
        pageno = ''
    try:
        keyword = request.GET['keyword']
    except:
        keyword = ''
    url = 'https://gogoanime.pe//search.html'+'?keyword='+keyword+'&page='+pageno
    response = requests.get(url, headers=headers,
                           impersonate='chrome110', timeout=20).text
    site = BeautifulSoup(response, 'html.parser')

    #Anime Movies
    news = site.find('div', class_='last_episodes').find_all('li')
    news_data = [{'name':r.p.a.text, 'image':r.div.a.img['src'], 'link':r.div.a['href'], 'episode':r.find_all('p')[1].text.strip(), 'sub':r.p.a.text.strip()[-4:-1]}  for r in news]
    try:
        page = site.find('ul', class_='pagination-list').find_all('li')
        pages = [{'link':p.a['href'], 'number':p.a.text} for p in page]
        if pageno == '':
            pageno = '1'
    except:
        pages = ''
        pageno = 'null'
    result = ' '.join(keyword.split('%20'))

    #Recent Release
    recrel_data = getrecent(site)
    #Season
    season_data = getseason(site)

    return render(request, 'search.html', {'season':season_data, 'lrel':news_data, 'popog':recrel_data, 'pages':pages, 'activepage':pageno, 'result':result, 'pagetitle':pagetitle})

def category(request, slug):
    increaseview('Category')
    url = 'https://gogoanime.pe/category/'+slug
    response = requests.get(url, headers=headers,
                           impersonate='chrome110', timeout=20).text
    site = BeautifulSoup(response, 'html.parser')

    #Category
    info = site.find('div', class_='anime_info_body_bg')
    image = info.img['src']
    title = info.h1.text
    pagetitle = title
    categoryview(pagetitle)
    others = info.find_all('p')[1:]
    type = others[0]
    type = [type.span.text, type.a['href'], type.a.text]
    summary = others[1]
    summary = [summary.span.text, summary.text.split('Plot Summary: ')[1]]
    gen = others[2]
    genre = list()
    genres = gen.find_all('a')
    for g in genres:
        gen = dict()
        gen['name'] = g.text
        gen['link'] = '/genre'+g['href'].split('genre')[1]
        genre.append(gen)
    released = others[3]
    released = [released.span.text, released.text.split(': ')[1]]
    status = others[4]
    status = [status.span.text, status.a.text]
    othername = others[5]
    othername = [othername.span.text, othername.text.split('Other name: ')[1]]
    animeinfo = {'image':image, 'title':title, 'type':type, 'summary':summary, 'genre':genre, 'released':released, 'status':status, 'othername':othername}
    #Episodes
    try:
        ep = request.GET['ep']
    except:
        ep = ''
    if status[1] != 'Upcoming':
        id = site.find('input', class_='movie_id')['value']
        default_ep = site.find('input', class_='default_ep')['value']
        alias_anime = site.find('input', class_='alias_anime')['value']
        eptab = site.find('ul', id='episode_page').find_all('li')
        tab = list()
        for et in eptab:
            tab.append(et.a.text)
        if ep == '':
            ep = tab[-1]
        start = ep.split('-')[0]
        try:
            end = ep.split('-')[1]
        except:
            end = start
        url = 'https://ajax.gogo-load.com/ajax/load-list-episode?ep_start='+start+'&ep_end='+end+'&id='+id+'&default_ep='+default_ep+'&alias='+alias_anime
        episodes = requests.get(url, headers=headers,
                           impersonate='chrome110', timeout=20).text
        episodes = BeautifulSoup(episodes, 'html.parser')
        try:
            episodes = episodes.find('ul', id='episode_related').find_all('li')
            episode = list()
            for epi in episodes:
                episode.append(['/episode'+epi.a['href'][1:]+'/?ep='+ep, epi.a.div.text, epi.a.find_all('div')[2].text])
        except:
            episode = ''
    else:
        episode = ''
        tab = ''

    #Recent Release
    recrel_data = getrecent(site)
    #Season
    season_data = getseason(site)

    return render(request, 'category.html', {'season':season_data, 'popog':recrel_data, 'animeinfo':animeinfo,'ep':tab, 'episode':episode, 'activeep':ep, 'pagetitle':pagetitle})

def episode(request, slug, ep):
    print(slug,ep)
    increaseview('Episode')
    url = 'https://ww4.gogoanime2.org/watch/'+slug+'/'+str(ep)
    print(url)
    response = requests.get(url, headers=headers,
                           impersonate='chrome110', timeout=20).text
    site = BeautifulSoup(response, 'html.parser')

    #Player
    title = site.find('div', class_='title_name').h2.text
    pagetitle = title
    episodeview(pagetitle)
    det = site.find('div', class_='anime_video_body_cate')
    category = [det.span.text, det.a['href'], det.a.text]
    animedetail = [det.div.span.text, det.div.a['href'], det.div.a.text]
    videolink = site.find('iframe')['src']
    animeinfo = {'title':title, 'category':category, 'animedetail':animedetail, 'videolink':videolink}
    activeepisode = title.split('Episode ')[1].split(' ')[0]
    try:
        ep = request.GET['ep']
    except:
        ep = ''
    try:
        next = site.find('div', class_='anime_video_body_episodes_r')
        next = ['/episode'+next.a['href']+'/?ep='+ep, next.a.text]
    except:
        next = ''
    try:
        prev = site.find('div', class_='anime_video_body_episodes_l')
        prev = ['/episode'+prev.a['href']+'/?ep='+ep, prev.a.text]
    except:
        prev = ''
    # download = site.find('li', class_='dowloads').a['href']
    #dsite = requests.get(download, headers=headers).text
    #dsite = BeautifulSoup(dsite, 'html.parser')
    #newvideolink = dsite.find_all('div', class_='dowload')[0].a['href']
    download = []
    #Episodes
    id = site.find('input', class_='movie_id')['value']
    default_ep = site.find('input', class_='default_ep')['value']
    alias_anime = site.find('input', class_='alias_anime')['value']
    # eptab = site.find('ul', id='episode_page').find_all('li')
    # tab = list()
    # for et in eptab:
    #     tab.append(et.a.text)
    # if ep == '':
    #     ep = tab[-1]
    # start = ep.split('-')[0]
    # try:
    #     end = ep.split('-')[1]
    # except:
    #     end = start
    tab=[]
    # url = 'https://ajax.gogo-load.com/ajax/load-list-episode?ep_start='+start+'&ep_end='+end+'&id='+id+'&default_ep='+default_ep+'&alias='+alias_anime
    # episodes = requests.get(url, headers=headers,
    #                        impersonate='chrome110', timeout=20).text
    # episodes = BeautifulSoup(episodes, 'html.parser')
    episodes = site
    episodes = episodes.find('ul', id='episode_related').find_all('li')
    episode = list()
    for epi in episodes:
        episode.append(['/episode'+epi.a['href'][1:]+'/?ep='+ep, epi.a.div.text, epi.a.find_all('div')[2].text, epi.a.div.text.split(' ')[1]])

    #Recent Release
    recrel_data = getrecent(site)
    #Season
    season_data = getseason(site)

    return render(request, 'episode.html', {'season':season_data, 'popog':recrel_data, 'animeinfo':animeinfo,'ep':tab, 'episode':episode, 'activeep':ep, 'activeepisode':activeepisode, 'next':next, 'prev':prev, 'download':download, 'pagetitle':pagetitle})


def genre(request, slug):
    increaseview('Genre')
    pagetitle = 'Genre '+slug.capitalize()
    try:
        pageno = request.GET['page']
    except:
        pageno = ''
    url = 'https://gogoanime.pe/genre/'+slug+'?page='+pageno
    response = requests.get(url, headers=headers,
                           impersonate='chrome110', timeout=20).text
    site = BeautifulSoup(response, 'html.parser')

    #Genre
    try:
        news = site.find('div', class_='last_episodes').find_all('li')
        news_data = [{'name':r.p.a.text, 'image':r.div.a.img['src'], 'link':r.div.a['href'], 'episode':r.find_all('p')[1].text.strip(), 'sub':r.p.a.text.strip()[-4:-1]}  for r in news]
        try:
            page = site.find('ul', class_='pagination-list').find_all('li')
            pages = [{'link':p.a['href'], 'number':p.a.text} for p in page]
            if pageno == '':
                pageno = '1'
        except:
            pages = ''
    except:
        news_data = ''
        pages = ''

    #Recent Release
    recrel_data = getrecent(site)
    #Season
    season_data = getseason(site)

    return render(request, 'genre.html', {'season':season_data, 'lrel':news_data, 'popog':recrel_data, 'pages':pages, 'activepage':pageno, 'genre':slug.capitalize(), 'pagetitle':pagetitle})


def subCategory(request, slug):
    increaseview('Sub Category')
    pagetitle = slug
    try:
        pageno = request.GET['page']
    except:
        pageno = ''
    url = 'https://gogoanime.pe/sub-category/'+slug+'?page='+pageno
    response = requests.get(url, headers=headers,
                           impersonate='chrome110', timeout=20).text
    site = BeautifulSoup(response, 'html.parser')

    #Genre
    try:
        news = site.find('div', class_='last_episodes').find_all('li')
        news_data = [{'name':r.p.a.text, 'image':r.div.a.img['src'], 'link':r.div.a['href'], 'episode':r.find_all('p')[1].text.strip(), 'sub':r.p.a.text.strip()[-4:-1]}  for r in news]
        try:
            page = site.find('ul', class_='pagination-list').find_all('li')
            pages = [{'link':p.a['href'], 'number':p.a.text} for p in page]
            if pageno == '':
                pageno = '1'
        except:
            pages = ''
    except:
        news_data = ''
        pages = ''

    #Recent Release
    recrel_data = getrecent(site)
    #Season
    season_data = getseason(site)

    return render(request, 'subcategory.html', {'season':season_data, 'lrel':news_data, 'popog':recrel_data, 'pages':pages, 'activepage':pageno, 'subcategory':slug.upper(), 'pagetitle':pagetitle})

def dmca(request):
    try:
        metadescription = meta['dmca']
    except:
        metadescription = ''
    pagetitle = 'DMCA'
    increaseview(pagetitle)
    url = 'https://gogoanime.pe/about-us.html'
    response = requests.get(url, headers=headers,
                           impersonate='chrome110', timeout=20).text
    site = BeautifulSoup(response, 'html.parser')

    #Recent Release
    recrel_data = getrecent(site)
    #Season
    season_data = getseason(site)

    return render(request, 'dmca.html', {'season':season_data, 'popog':recrel_data, 'pagetitle':pagetitle, 'metadescription':metadescription})


def aboutUs(request):
    try:
        metadescription = meta['about']
    except:
        metadescription = ''
    pagetitle='About Us'
    increaseview(pagetitle)
    url = 'https://gogoanime.pe/about-us.html'
    response = requests.get(url, headers=headers,
                           impersonate='chrome110', timeout=20).text
    site = BeautifulSoup(response, 'html.parser')

    #Recent Release
    recrel_data = getrecent(site)
    #Season
    season_data = getseason(site)

    return render(request, 'about.html', {'season':season_data, 'popog':recrel_data, 'pagetitle':pagetitle, 'metadescription':metadescription})

def contactUs(request):
    if request.method == 'POST':
        fname = request.POST['fname']
        lname = request.POST['lname']
        message = request.POST['message']
        email = request.POST['email']
        import smtplib
        from email.mime.text import MIMEText

        msge = 'Name: '+fname+' '+lname+'\nEmail: '+email+'\nMessage: '+message
        msg = MIMEText(msge)

        sender = 'admin@owoanime.com'
        receiver = 'contact@owoanime.com'
        msg['Subject'] = 'Message From '+fname+' '+lname
        msg['From'] = sender
        msg['To'] = receiver

        s = smtplib.SMTP_SSL('server294.web-hosting.com', 465)
        s.login("admin@owoanime.com", "owoanime@1414")
        s.send_message(msg)
        s.quit()
    try:
        metadescription = meta['contact']
    except:
        metadescription = ''
    pagetitle = 'Contact Us'
    increaseview(pagetitle)
    url = 'https://gogoanime.pe/about-us.html'
    response = requests.get(url, headers=headers,
                           impersonate='chrome110', timeout=20).text
    site = BeautifulSoup(response, 'html.parser')

    #Recent Release
    recrel_data = getrecent(site)
    #Season
    season_data = getseason(site)

    return render(request, 'contact.html', {'season':season_data, 'popog':recrel_data, 'pagetitle':pagetitle, 'metadescription':metadescription})

def boruto(request):
    pagetitle='Boruto Next Generation'
    url = 'https://gogoanime.pe/about-us.html'
    response = requests.get(url, headers=headers,
                           impersonate='chrome110', timeout=20).text
    site = BeautifulSoup(response, 'html.parser')

    #Recent Release
    recrel_data = getrecent(site)
    #Season
    season_data = getseason(site)

    return render(request, 'blog/boruto.html', {'season':season_data, 'popog':recrel_data, 'pagetitle':pagetitle})

def naruto(request):
    pagetitle='Naruto'
    url = 'https://gogoanime.pe/about-us.html'
    response = requests.get(url, headers=headers,
                           impersonate='chrome110', timeout=20).text
    site = BeautifulSoup(response, 'html.parser')

    #Recent Release
    recrel_data = getrecent(site)
    #Season
    season_data = getseason(site)

    return render(request, 'blog/naruto.html', {'season':season_data, 'popog':recrel_data, 'pagetitle':pagetitle})

def shippuden(request):
    pagetitle='Naruto Shippuden'
    url = 'https://gogoanime.pe/about-us.html'
    response = requests.get(url, headers=headers,
                           impersonate='chrome110', timeout=20).text
    site = BeautifulSoup(response, 'html.parser')

    #Recent Release
    recrel_data = getrecent(site)
    #Season
    season_data = getseason(site)

    return render(request, 'blog/shippuden.html', {'season':season_data, 'popog':recrel_data, 'pagetitle':pagetitle})

def hunter(request):
    pagetitle='Hunter X Hunter'
    url = 'https://gogoanime.pe/about-us.html'
    response = requests.get(url, headers=headers,
                           impersonate='chrome110', timeout=20).text
    site = BeautifulSoup(response, 'html.parser')

    #Recent Release
    recrel_data = getrecent(site)
    #Season
    season_data = getseason(site)

    return render(request, 'blog/hunter.html', {'season':season_data, 'popog':recrel_data, 'pagetitle':pagetitle})

def tokyo(request):
    pagetitle='Tokyo Revengers'
    url = 'https://gogoanime.pe/about-us.html'
    response = requests.get(url, headers=headers,
                           impersonate='chrome110', timeout=20).text
    site = BeautifulSoup(response, 'html.parser')

    #Recent Release
    recrel_data = getrecent(site)
    #Season
    season_data = getseason(site)

    return render(request, 'blog/tokyo.html', {'season':season_data, 'popog':recrel_data, 'pagetitle':pagetitle})

def demon(request):
    pagetitle='Demon Slayer'
    url = 'https://gogoanime.pe/about-us.html'
    response = requests.get(url, headers=headers,
                           impersonate='chrome110', timeout=20).text
    site = BeautifulSoup(response, 'html.parser')

    #Recent Release
    recrel_data = getrecent(site)
    #Season
    season_data = getseason(site)

    return render(request, 'blog/demon.html', {'season':season_data, 'popog':recrel_data, 'pagetitle':pagetitle})

def sitemap(request):
    return render(request, 'sitemap.xml')
    
def ads(request):
    return render(request, 'ads.txt')
