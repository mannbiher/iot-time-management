BASE_URL = "https://leetcode.com/"
LOGIN_URL = "https://leetcode.com/accounts/login/"
GRAPHQL_URL = "https://leetcode.com/graphql"
ALL_URL = "https://leetcode.com/api/problems/$category_slug/"
PROBLEM_URL = "https://leetcode.com/problems/$slug"
PROBLEM_SET_URL = "https://leetcode.com/problemset/all/"
HOST = "leetcode.com"


GRAPH_QL = {
    'Submissions': "query Submissions($offset: Int!, $limit: Int!, $lastKey: String, $questionSlug: String!) {\n  submissionList(offset: $offset, limit: $limit, lastKey: $lastKey, questionSlug: $questionSlug) {\n    lastKey\n    hasNext\n    submissions {\n      id\n      statusDisplay\n      lang\n      runtime\n      timestamp\n      url\n      isPending\n      memory\n      __typename\n    }\n    __typename\n  }\n}\n"
}

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:88.0) Gecko/20100101 Firefox/88.0"

DYNAMODB_TABLE = 'cs498_leetcode'

USER_TZ = 'US/Eastern'
