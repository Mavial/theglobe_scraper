import logging
import json
import datetime


class DataHandler():
    def __init__(self, response, settings):
        self.logger = logging.getLogger(__name__)
        self.settings = settings
        self.response = response
        self.get_func = {}
        self.get_func['name'] = self._get_name_
        self.get_func['title'] = self._get_title_
        self.get_func['title_detail'] = self._get_title_detail_
        self.get_func['author'] = self._get_author_
        self.get_func['summary'] =  self._get_summary_
        self.get_func['content'] = self._get_content_
        self.get_func['tags'] = self._get_tags_
        self.get_func['urlToImg'] = self._get_urlToImg_
        self.get_func['publishedAt'] = self._get_publishedAt_
        self.get_func['modifiedAt'] = self._get_modifiedAt_

    def _get_all_data_(self):
        schema = self.__get_schema_()
        article = self.__convert_data_(schema)
        return article

    def __get_schema_(self):
        SCHEMA_SELECTORS = self.settings.getlist('SCHEMA_SELECTORS')
        for item in SCHEMA_SELECTORS:
            try:
                schema = self.response.xpath(item).get()
            except Exception:
                continue
            else:
                try:
                    schema = json.loads(schema)
                except TypeError:
                    self.logger.debug(f"Couldn't find schema dict in: {self.response.url}")
                    self.schema_type = self.settings.getdict('DEFAULT')
                else:
                    self.logger.debug(f"Schema {schema['@type']} found in: {self.response.url}")
                    # Check if schema type exist in settings
                    self.__check_shema_(schema)
                return schema
        self.logger.critical(f"None of the SCHEMA_SELECTORS worked for: {self.response.url} ")
        return False


    def __check_shema_(self, schema):
        self.schema_type = self.settings.getdict(schema['@type'].upper())
        if not self.schema_type:
            self.logger.warning(f"There is no existing Schema sample for the {schema['@type']} type.")
            self.schema_type = self.settings.getdict('DEFAULT')


    def __convert_data_(self, schema):
        keys = self.schema_type.keys()
        data = {}
        for key in keys:
            if self.schema_type[key]['list'] == []:
                data[key] = self.__convert_response_xpath_(key)
            else:
                value = schema
                for x in self.schema_type[key]['list']:
                    try:
                        value = value[x]
                    except Exception:
                        self.logger.warning(f"Something went wrong when trying to access the downloaded schema. url = {self.response.url}, key = {key}/{x}", exc_info=True)
                        value = self.__convert_response_xpath_(key)
                        break
                if key == "publishedAt" or key == "modifiedAt":
                    value = self._date_formatter_(value)
                data[key] = value
        """TODO put a schema check here (pip install schema / pip install jsonschema)"""
        return data


    def __convert_response_xpath_(self, key):
        try:
            value = self.get_func[key]()
        except KeyError:
            self.logger.error(f"No function could be found with the '{key}' key.")
            return "N/A"
        else:
            if value == "N/A":
                self.logger.debug(f"None of the Selectors ({key}) worked for {self.response.url}")
            return value


    def _get_name_(self):
        """Get the name of the Newspaper."""
        NAME_SELECTORS = self.settings.getlist('NAME_SELECTORS')
        for item in NAME_SELECTORS:
            try:
                name = self.response.xpath(item).get()
            except Exception:
                continue
            else:
                return name
        return("N/A")


    def _get_title_(self):
        """Get the title of the article."""
        TITLE_SELECTORS = self.settings.getlist('TITLE_SELECTORS')
        for item in TITLE_SELECTORS:
            try:
                title = self.response.xpath(item).get()
            except Exception:
                continue
            else:
                return title
        return("N/A")


    def _get_title_detail_(self):
        """
        Get a detailed title of the article.
        Mostly called "description".
        """
        TITLE_DETAIL_SELECTORS = self.settings.getlist('TITLE_DETAIL_SELECTORS')
        for item in TITLE_DETAIL_SELECTORS:
            try:
                title_detail = self.response.xpath(item).get()
            except Exception:
                continue
            else:
                return title_detail
        return("N/A")

    def _get_author_(self):
        """
        Get the author of the article.
        This can sometimes be a bit tricky:
        BBC only has itself as author of the article.
        """
        AUTHOR_SELECTORS = self.settings.getlist('AUTHOR_SELECTORS')
        for item in AUTHOR_SELECTORS:
            try:
                author = self.response.xpath(item).get()
            except Exception:
                continue
            else:
                return author
        return("N/A")

    def _get_summary_(self):
        """
        Get a summary of the article.
        Sometimes the articles only have a title and description, but no summary.
        """
        SUMMARY_SELECTORS = self.settings.getlist('SUMMARY_SELECTORS')
        for item in SUMMARY_SELECTORS:
            try:
                summary = self.response.xpath(item).get()
            except Exception:
                continue
            else:
                return summary
        return("N/A")


    def _get_content_(self):
        """
        Get the whole content of the article.
        TODO This is still pretty hard to do
        regarding to the fact that there are many different article types.
        """
        CONTENT_SELECTORS = self.settings.getlist('CONTENT_SELECTORS')
        for item in CONTENT_SELECTORS:
            try:
                content = self.response.xpath(item).get()
            except Exception:
                continue
            else:
                return content
        return("N/A")


    def _get_tags_(self):
        """
        Get the keywords/tags.
        Some websites have keyword/tags regardning to the articles topic.
        """
        KEYWORD_SELECTORS = self.settings.getlist('KEYWORD_SELECTORS')
        for item in KEYWORD_SELECTORS:
            try:
                keywords = self.response.xpath(item).get()
            except Exception:
                continue
            else:
                return keywords
        return("N/A")


    def _get_urlToImg_(self):
        """
        Get the main Image of the article.
        Articles can have more than one picture,
        but this method only wants to get the main picture.
        """
        IMAGE_SELECTORS = self.settings.getlist('IMAGE_SELECTORS')
        for item in IMAGE_SELECTORS:
            try:
                url_to_img = self.response.xpath(item).get()
            except Exception:
                continue
            else:
                return url_to_img
        return("N/A")


    def _get_publishedAt_(self):
        """
        Get the published date of the article.
        Articles can have many different date data.
        Most important, though, is when the article got published.
        """
        PUB_DATE_SELECTORS = self.settings.getlist('PUB_DATE_SELECTORS')

        for item in PUB_DATE_SELECTORS:
            try:
                response_date = self.response.xpath(item).get()
            except Exception:
                continue
            else:
                form_date = self._date_formatter_(response_date)
                if form_date:
                    return form_date
        return("N/A")


    def _get_modifiedAt_(self):
        """
        Get the modified date of the article.
        Articles can have many different date data.
        """
        MOD_DATE_SELECTORS = self.settings.getlist('MOD_DATE_SELECTORS')

        for item in MOD_DATE_SELECTORS:
            try:
                response_date = self.response.xpath(item).get()
            except Exception:
                continue
            else:
                form_date = self._date_formatter_(response_date)
                if form_date:
                    return form_date
        return("N/A")


    def _date_formatter_(self, date):
        DATE_FORMATS = self.settings.getlist('DATE_FORMATS')
        if date == None:
            return False
        for format in DATE_FORMATS:
            try:
                form_date = datetime.datetime.strptime(date, format)
            except Exception:
                continue
            else:
                return form_date
        self.logger.error(f"None of the Date Formats did work for '{date}'!")
        return date