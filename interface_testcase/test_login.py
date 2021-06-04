#!/usr/bin/env python3
# coding=utf-8
import pytest


class TestLogin:

    def test_01(self):
        print('ceshi')

    @pytest.mark.run(order=1)
    def test_02(self):
        print('ceshi2')
        assert 1 == 2

if __name__ == '__main__':
    pytest.main(['-vs'])
