import re

error_msg = """
'>
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
        <div theme="">
            <section class="maincontainer">
                <div class="container is-page">
                    <header class="navigation-header">
                    </header>
                    <h4>ERROR: invalid input syntax for type integer: "meygkq9f3q5yxt1oq415"</h4>
                    <p class=is-warning>ERROR: invalid input syntax for type integer: "meygkq9f3q5yxt1oq415"</p>
                </div>
            </section>
        </div>
    </body>
</html>
"""

pattern = r'ERROR: invalid input syntax for type integer:\s*"([^"]+)"'
match = re.search(pattern, error_msg)

if match:
    value = match.group(1)
    print("Captured:", value)  # 輸出: meygkq9f3q5yxt1oq415
else:
    print("No match")
