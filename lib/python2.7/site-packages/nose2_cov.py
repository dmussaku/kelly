"""Coverage plugin for nose2."""

import nose2


class CovPlugin(nose2.events.Plugin):

    configSection = 'cov'
    commandLineSwitch = ('C', 'with-cov', 'Turn on coverage reporting')

    def __init__(self):
        """Get our config and add our command line arguments."""

        self.conSource = self.config.as_list('cov', [])
        self.conReport = self.config.as_list('cov-report', [])
        self.conConfig = self.config.as_str('cov-config', '').strip()

        group = self.session.pluginargs
        group.add_argument('--cov', action='append', default=[], metavar='PATH',
                           dest='cov_source',
                           help='Measure coverage for filesystem path (multi-allowed)')
        group.add_argument('--cov-report', action='append', default=[], metavar='TYPE',
                           choices=['term', 'term-missing', 'annotate', 'html', 'xml'],
                           dest='cov_report',
                           help='Generate selected reports, available types: term, term-missing, annotate, html, xml (multi-allowed)')
        group.add_argument('--cov-config', action='store', default='', metavar='FILE',
                           dest='cov_config',
                           help='Config file for coverage, default: .coveragerc')

    def handleArgs(self, event):
        """Get our options in order command line, config file, hard coded."""

        self.covSource = event.args.cov_source or self.conSource or ['.']
        self.covReport = event.args.cov_report or self.conReport or ['term']
        self.covConfig = event.args.cov_config or self.conConfig or '.coveragerc'

    def startTestRun(self, event):
        """Only called if active so start coverage."""

        import cov_core
        self.covController = cov_core.Central(self.covSource, self.covReport, self.covConfig)
        self.covController.start()

    def afterSummaryReport(self, event):
        """Only called if active so stop coverage and produce reports."""

        self.covController.finish()
        self.covController.summary(event.stream)
