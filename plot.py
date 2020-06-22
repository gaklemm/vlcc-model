import matplotlib.pyplot as plt
import seaborn as sns
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()


class Graph(object):
    """
    Graphing class containing various plotting methods.
    """

    def __init__(self, data, name, value):
        """
        :param data: 2-column dataframe for x and y
        :param name: description of data to plot
        :param value: name of y data column
        """
        self.title = name
        self.data = data
        self.graph = None
        self.value = value

    def plot(self):
        """
        :return: seaborn lineplot
        """
        # set plot style
        sns.set_style("ticks")
        sns.despine()
        # create plot
        self.graph = sns.lineplot(data=self.data)
        self.graph.set(title=self.title, xlabel='Date', ylabel=self.value)
        plt.show()

    def save(self, filetype='html'):
        """
        :param name2: (optional) name of secondary y data column
        :param filetype: file type ('png', 'jpg', 'svg', 'tiff', 'pdf'...)
        :return: plot files
        """
        fig = self.graph.get_figure()
        fig.savefig('output/' + self.title + filetype)
