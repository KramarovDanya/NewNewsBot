import json
from bs4 import BeautifulSoup
import aiohttp
import asyncio
import aiofiles
import argparse
import csv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fake_useragent import UserAgent
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class Requester:
    def __init__(self) -> None:
        self.session = aiohttp.ClientSession()
        self.user_agent = UserAgent()

    def get_headers(self) -> Dict[str, str]:
        return {
            'User-Agent': self.user_agent.random
        }

    async def get(self, url: str) -> str:
        async with self.session.get(url, headers=self.get_headers()) as response:
            response.raise_for_status()
            return await response.text()

    async def post(self, url: str, params: Optional[Dict[str, Any]] = None) -> str:
        async with self.session.post(url, headers=self.get_headers(), params=params) as response:
            response.raise_for_status()
            return await response.text()

    async def close(self) -> None:
        await self.session.close()


class BaseParser(ABC):
    def __init__(self, requester: Requester) -> None:
        self.requester = requester

    @abstractmethod
    async def get_article_links(self, page_data: Dict[str, Any]) -> List[str]:
        pass

    @abstractmethod
    async def parse_article(self, html: str) -> Dict[str, str]:
        pass


# class InterexchangeParse(BaseParser):
#     BASE_URL = "https://www.interexchange.org/wp-admin/admin-ajax.php"
#
#     async def get_article_links(self, page_data: Dict[str, Any]) -> List[str]:
#         links = []
#         html = await self.requester.post(self.BASE_URL, params=page_data)
#         html = json.loads(html)
#         html = html['content']
#         # html.replace(r'\/', '/')
#         # html = codecs.decode(html, "unicode_escape")
#         soup = BeautifulSoup(html, 'html.parser')
#         for a_tag in soup.find_all('a', class_='elementor-button-link'):
#             href = a_tag['href']
#             full_url = href if href.startswith("http") else f"https://www.interexchange.org{href}"
#             links.append(full_url)
#         return links
#
#     async def parse_article(self, html: str) -> Dict[str, str]:
#         soup = BeautifulSoup(html, 'html.parser')
#         title = soup.find('h1').get_text(strip=True) if soup.find('h1') else "Без заголовка"
#         content = "\n".join([p.get_text(strip=True) for p in soup.find_all('p')])
#         return {
#             'title': title,
#             'content': content,
#         }
#
#     async def fetch_all_articles(self) -> List[Dict[str, str]]:
#         articles = []
#         page_number = 1
#
#         while True:
#             try:
#                 page_data = {
#                     "action": "jet_smart_filters",
#                     "provider": "jet-engine/blog-list",
#                     "settings[lisitng_id]": 962,
#                     "props[page]":  page_number,
#                     "props[query_type]": 'posts',
#                     "paged": page_number + 1,
#
#                 }
#                 print(f"Fetching page {page_number}...")
#
#                 links = await self.get_article_links(page_data)
#                 if not links:
#                     print(f"No links found on page {page_number}.")
#                     break
#
#                 for link in links:
#                     try:
#                         html = await self.requester.post(link)
#                         article_data = await self.parse_article(html)
#                         article_data['url'] = link
#                         articles.append(article_data)
#                         print(f"Successfully parsed: {article_data['title']}")
#                     except Exception as e:
#                         print(f"Error parsing article {link}: {e}")
#
#                 # Check for the next page
#                 # html = await self.requester.post(self.BASE_URL, params=page_data)
#                 # soup = BeautifulSoup(html, 'html.parser')
#                 # next_page = soup.find('div', class_='jet-filters-pagination__link', string=str(page_number + 1))
#                 # if next_page:
#                 page_number += 1
#                 # else:
#                 #     break
#
#             except Exception as e:
#                 print(f"Error fetching page {page_number}: {e}")
#                 break
#
#         return articles


class AuPairUSABlogParser(BaseParser):
    BASE_URL = "https://blog.aupairusa.org/au-pairs/"

    async def get_article_links(self, html: str) -> List[str]:
        soup = BeautifulSoup(html, 'html.parser')
        links = []
        for a_tag in soup.find_all('h2', class_='entry-title'):
            link_tag = a_tag.find('a')
            if link_tag and link_tag.has_attr('href'):
                href = link_tag['href']
                full_url = href if href.startswith("http") else href
                links.append(full_url)
        return links

    async def parse_article(self, html: str) -> Dict[str, str]:
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.find('h1').get_text(strip=True) if soup.find('h1') else "Без заголовка"
        content = "\n".join([p.get_text(strip=True) for p in soup.find_all('p')])
        return {
            'title': title,
            'content': content,
        }

    async def get_all_pages(self) -> List[str]:
        pages = set([self.BASE_URL])
        html = await self.requester.post(self.BASE_URL)
        soup = BeautifulSoup(html, 'html.parser')
        pagination_div = soup.find('div', class_='col-md-8 page_navi')
        if pagination_div:
            last_page_link = pagination_div.find('a', class_='last')
            if last_page_link and last_page_link.has_attr('href'):
                last_page_url = last_page_link['href']
                total_pages = int(last_page_url.rstrip('/').split('/')[-1])
                for i in range(1, total_pages + 1):
                    page_url = f"https://blog.aupairusa.org/au-pairs/page/{i}/"
                    pages.add(page_url)
        return sorted(pages)

    async def fetch_all_articles(self) -> List[Dict[str, str]]:
        articles = []
        pages = await self.get_all_pages()

        for page in pages:
            try:
                html = await self.requester.post(page)
                links = await self.get_article_links(html)
                for link in links:
                    try:
                        article_html = await self.requester.post(link)
                        article_data = await self.parse_article(article_html)
                        article_data['url'] = link
                        articles.append(article_data)
                        print(f"Successfully parsed: {article_data['title']}")
                    except Exception as e:
                        print(f"Error parsing article {link}: {e}")
            except Exception as e:
                print(f"Error fetching page {page}: {e}")

        return articles


class IECParse(BaseParser):
    BASE_URL = "https://iec.ru"

    async def get_article_links(self, html: str) -> List[str]:
        soup = BeautifulSoup(html, 'html.parser')
        links = []
        for a_tag in soup.find_all('a', 'wrapper'):
            href = a_tag['href']
            full_url = self.BASE_URL + href if not href.startswith("http") else href
            links.append(full_url)
        return list(set(links))
    
    async def parse_article(self, html: str) -> Dict[str, str]:
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.find('h1').get_text(strip=True) if soup.find('h1') else "Без заголовка"
        content = "\n".join([p.get_text(strip=True) for p in soup.find_all('p')])
        return {
            'title': title,
            'content': content
        }

    # async def fetch_all_articles(self) -> List[Dict[str, str]]:
    #     articles = []
    #     # main_page_html = await self.requester.post(self.BASE_URL)
    #     # links = await self.get_article_links(main_page_html)
    #     for link in links:
    #         try:
    #             article_html = await self.requester.post(link)
    #             article_data = await self.parse_article(article_html)
    #             article_data['url'] = link
    #             articles.append(article_data)
    #             print(f"Successfully parsed: {article_data['title']}")
    #         except Exception as e:
    #             print(f"Error parsing article {link}: {e}")

    #     return articles
    
    async def fetch_all_articles(self, links: List[str]) -> List[Dict[str, str]]:
        """
        Загружает полный текст статей по ссылкам.
        """
        articles = []
        for link in links:
            try:
                article_html = await self.requester.post(link)
                article_data = await self.parse_article(article_html)
                article_data['url'] = link
                articles.append(article_data)
                print(f"Successfully parsed: {article_data['title']}")
            except Exception as e:
                print(f"Error parsing article {link}: {e}")

        return articles


class InterexchangeInternationalStaffParse(BaseParser):
    BASE_URL = "https://www.interexchange.org/programs/work-travel-usa/international-staff/resources/"

    def __init__(self, requester: Requester) -> None:
        super().__init__(requester)

    async def get_article_links(self, html: str) -> List[str]:
        soup = BeautifulSoup(html, 'html.parser')
        links = []

        # Extract links from h3 > a within elementor-widget-container
        for container in soup.select('.elementor-widget-container'):
            for h3_tag in container.select('h3 > a'):
                href = h3_tag['href']
                full_url = href if href.startswith("http") else f"https://www.interexchange.org{href}"
                links.append(full_url)

            # Extract links from li > a, excluding those containing # and within elementor-nav-menu__container
            for li_tag in container.select('li > a'):
                if "elementor-nav-menu__container" not in li_tag.get("class", ""):
                    href = li_tag['href']
                    if "#" not in href:
                        full_url = href if href.startswith("http") else f"https://www.interexchange.org{href}"
                        links.append(full_url)

        return links

    async def parse_article(self, html: str) -> Dict[str, str]:
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.find('h1').get_text(strip=True) if soup.find('h1') else "No Title"
        content = "\n".join([p.get_text(strip=True) for p in soup.find_all('p')])
        return {
            'title': title,
            'content': content,
        }

    async def fetch_all_articles(self) -> List[Dict[str, str]]:
        articles = []

        try:
            html = await self.requester.get(self.BASE_URL)
            links = await self.get_article_links(html)

            for link in links:
                try:
                    article_html = await self.requester.get(link)
                    article_data = await self.parse_article(article_html)
                    article_data['url'] = link
                    articles.append(article_data)
                    print(f"Successfully parsed: {article_data['title']}")
                except Exception as e:
                    print(f"Error parsing article {link}: {e}")

        except Exception as e:
            print(f"Error fetching articles: {e}")

        return articles


async def load_existing_links(file_path: str) -> set:
    """
    Загружает ссылки из существующего файла.
    """
    try:
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
            return {line.split(',')[-1].strip() for line in (await file.read()).splitlines()[1:]}
    except FileNotFoundError:
        return set()  # Если файл не найден, возвращаем пустой набор


async def save_articles(file_path: str, articles: list):
    """
    Сохраняет статьи в файл.
    """
    async with aiofiles.open(file_path, 'a', encoding='utf-8', newline='') as file:
        for article in articles:
            content_clean = article['content'].replace(',', ' ').replace('\n', ' ')
            await file.write(f"{article['title']},{content_clean},{article['url']}\n")


async def fetch_and_save_articles(initial_run=False):
    """
    Основная функция парсинга и сохранения статей.
    """
    file_path = 'combined_articles.csv'
    requester = Requester()
    parser = IECParse(requester)

    try:
        # Загружаем существующие ссылки (только для schedule)
        existing_links = set()
        if not initial_run:
            existing_links = await load_existing_links(file_path)
            print(f"Загружено {len(existing_links)} существующих ссылок.")

        # Получаем все ссылки с главной страницы
        main_page_html = await requester.post(parser.BASE_URL)
        current_links = await parser.get_article_links(main_page_html)

        # Определяем новые ссылки
        if initial_run:
            new_links = current_links  # Для initial загружаем все статьи
        else:
            new_links = [link for link in current_links if link not in existing_links]

        print(f"Найдено {len(new_links)} новых статей.")

        # Загружаем данные только для новых ссылок
        if new_links:
            new_articles = await parser.fetch_all_articles(new_links)  # Исправлено: передаём только список ссылок

            # Сохраняем новые статьи
            await save_articles(file_path, new_articles)
            print(f"Сохранено {len(new_articles)} новых статей в {file_path}")
        else:
            print("Новых статей не найдено.")

    except Exception as e:
        print(f"Execution error: {e}")

    finally:
        await requester.close()


async def main():
    """
    Основная функция для работы в зависимости от режима.
    """
    parser = argparse.ArgumentParser(description="Парсинг статей с сайта и управление расписанием.")
    parser.add_argument('--mode', choices=['initial', 'schedule'], required=True, help="Режим работы: 'initial' для первого прохода, 'schedule' для планировщика.")
    args = parser.parse_args()

    if args.mode == 'initial':
        print("Запущен режим первого прохода (initial).")
        await fetch_and_save_articles(initial_run=True)
    elif args.mode == 'schedule':
        print("Запущен режим расписания (schedule).")
        scheduler = AsyncIOScheduler()
        scheduler.add_job(fetch_and_save_articles, "interval", hours=1)  # Запуск каждые 1 час
        scheduler.start()

        print("Планировщик запущен. Для ручного запуска введите 'Y'. Нажмите Ctrl+C для остановки.")
        try:
            while True:
                user_input = input("Запустить парсинг вручную? (Y/N): ").strip().lower()
                if user_input == 'y':
                    print("Ручной запуск парсинга...")
                    await fetch_and_save_articles(initial_run=False)
                    print("Ручной запуск завершён.")
                elif user_input == 'n':
                    print("Ручной запуск отменён.")
                await asyncio.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            print("Остановка планировщика.")
            scheduler.shutdown()


if __name__ == '__main__':
    asyncio.run(main())
