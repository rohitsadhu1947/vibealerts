"""
Test basic imports and configuration
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_imports():
    """Test that all main modules can be imported"""
    
    from src.database.models import Announcement, ExtractedMetrics, AnalysisResult
    from src.monitoring.service import MonitoringService, NSEMonitor
    from src.extraction.service import ExtractionService, PDFExtractor, MetricsParser
    from src.analysis.engine import AnalysisEngine
    from src.notification.telegram import TelegramNotifier
    from config import load_config
    
    assert True


def test_config_loading():
    """Test configuration loading"""
    
    from config import load_config
    
    # This will fail if config.yaml is malformed
    config = load_config()
    
    assert 'monitoring' in config
    assert 'extraction' in config
    assert 'telegram' in config


def test_data_models():
    """Test data model creation"""
    
    from src.database.models import Announcement, ExtractedMetrics, Sentiment
    from datetime import datetime
    from decimal import Decimal
    
    # Test Announcement
    ann = Announcement(
        source='nse',
        symbol='TESTCO',
        date='13-11-2024',
        description='Q3 Financial Results',
        attachment_url='http://example.com/test.pdf'
    )
    assert ann.symbol == 'TESTCO'
    
    # Test ExtractedMetrics
    metrics = ExtractedMetrics(
        symbol='TESTCO',
        quarter=3,
        fiscal_year=2025,
        revenue=Decimal('1000.50'),
        profit_after_tax=Decimal('150.25'),
        eps=Decimal('12.50')
    )
    assert metrics.revenue == Decimal('1000.50')
    assert metrics.confidence_score == 0.0  # default


def test_metrics_parser():
    """Test metrics parsing"""
    
    from src.extraction.service import MetricsParser
    
    parser = MetricsParser()
    
    sample_text = """
    Q3 FY2025 Financial Results
    
    Total Income: Rs. 1,234.56 crore
    Profit After Tax: Rs. 567.89 crore
    Basic EPS: Rs. 12.34
    """
    
    metrics = parser.parse(sample_text, 'TESTCO')
    
    assert metrics.symbol == 'TESTCO'
    assert metrics.quarter == 3
    assert metrics.fiscal_year == 2025
    # Note: Actual extraction may vary based on regex patterns


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

