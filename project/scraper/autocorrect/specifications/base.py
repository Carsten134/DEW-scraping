from bs4 import BeautifulSoup
from selenium.webdriver import Firefox

class PageSpecification:
  """
  Base class for html page specifications.

  This class follows the [specification design pattern](https://en.wikipedia.org/wiki/Specification_pattern)

  If you want a scraper to be as self sufficient as possible,
  you need it to check conditions that are needed for operations to be carried out.

  This class helps to achieve that.
  """
  def __init__(self, candidate_driver: Firefox):
    self.candidate_driver = candidate_driver
    self.candidate_soup = BeautifulSoup(candidate_driver.page_source, "html.parser")

  def is_satisfied(self) -> bool:
    raise NotImplementedError("method is_satisfied is not implemented")


class CompositeSpecification:
  def validate(self):
    raise NotImplementedError("method validate must be implemented")


class AndSpecification(CompositeSpecification):
  def __init__(self, conditions: list):
    self.conditions = conditions
  
  def validate(self) -> bool:
    return all([condition.is_satisfied() for condition in self.condtions])


class OrSpecification(CompositeSpecification):
  def __init__(self, conditions: list):
    self.conditions = conditions
  
  def validate(self) -> bool:
    return any([condition.is_satisfied() for condition in self.conditions])