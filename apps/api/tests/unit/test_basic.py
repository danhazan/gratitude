"""
Basic tests to verify test infrastructure works.
"""

import pytest


def test_basic_math():
    """Test basic arithmetic."""
    assert 1 + 1 == 2


def test_string_operations():
    """Test string operations."""
    assert "hello" + " " + "world" == "hello world"


@pytest.mark.asyncio
async def test_async_function():
    """Test async function works."""
    result = await async_function()
    assert result == "async works"


async def async_function():
    """Simple async function for testing."""
    return "async works"


class TestBasicClass:
    """Test class structure."""
    
    def test_instance_method(self):
        """Test instance method."""
        assert self.__class__.__name__ == "TestBasicClass"
    
    @pytest.mark.asyncio
    async def test_async_instance_method(self):
        """Test async instance method."""
        result = await async_function()
        assert result == "async works" 