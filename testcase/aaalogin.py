#!/usr/bin/env python3
# coding=utf-8
import pytest


class TestLogin:

    @pytest.mark.smoke
    def test_01(self):
        print('ceshi01')

    def test_02(self):
        print('ceshi02')


if __name__ == '__main__':
    pytest.main(['-vs'])
