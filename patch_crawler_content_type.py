with open("spyder_app/crawler.py", "r") as f:
    content = f.read()

new_content = content.replace("""                with response:
                    response.raise_for_status()

                    content_chunks = []
                    downloaded_size = 0
                    max_size = 10 * 1024 * 1024  # 10 MB

                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            downloaded_size += len(chunk)
                            if downloaded_size > max_size:
                                print(f"Skipping {url}: Response exceeded 10MB limit.")
                                content_chunks = None
                                break
                            content_chunks.append(chunk)""", """                with response:
                    response.raise_for_status()

                    content_type = response.headers.get("Content-Type", "")
                    if "text/html" not in content_type:
                        print(f"Skipping {url}: Unsupported Content-Type {content_type}")
                        continue

                    content_chunks = []
                    downloaded_size = 0
                    max_size = 10 * 1024 * 1024  # 10 MB

                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            downloaded_size += len(chunk)
                            if downloaded_size > max_size:
                                print(f"Skipping {url}: Response exceeded 10MB limit.")
                                content_chunks = None
                                break
                            content_chunks.append(chunk)""")


new_content = new_content.replace("""            with response:
                response.raise_for_status()

                content_chunks = []
                downloaded_size = 0
                max_size = 10 * 1024 * 1024  # 10 MB

                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        downloaded_size += len(chunk)
                        if downloaded_size > max_size:
                            print(f"Skipping {news_url}: Response exceeded 10MB limit.")
                            content_chunks = None
                            break
                        content_chunks.append(chunk)""", """            with response:
                response.raise_for_status()

                content_type = response.headers.get("Content-Type", "")
                if "text/html" not in content_type:
                    print(f"Skipping {news_url}: Unsupported Content-Type {content_type}")
                    return

                content_chunks = []
                downloaded_size = 0
                max_size = 10 * 1024 * 1024  # 10 MB

                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        downloaded_size += len(chunk)
                        if downloaded_size > max_size:
                            print(f"Skipping {news_url}: Response exceeded 10MB limit.")
                            content_chunks = None
                            break
                        content_chunks.append(chunk)""")

with open("spyder_app/crawler.py", "w") as f:
    f.write(new_content)
