#!/usr/bin/env python
# coding: utf-8

import html

import requests
from requests.auth import HTTPBasicAuth

import seaborn as sns
import matplotlib.pyplot as plt

import plotly.io as pio
import plotly.express as px

import numpy as np

import pandas as pd

import streamlit as st

pio.templates.default = "plotly_white"


# change
def x(l, k, v): l[html.unescape(k)] = v


# get assets of type and status from a given community
def getAssets(collibra, communities, assetTypes, statuses):
    viewConfig = {
        "ViewConfig": {
            "maxCountLimit": "-1",
            "Resources": {
                "Asset": {
                    "name": "Assets",
                    "Id": {
                        "name": "assetId"
                    },
                    "DisplayName": {
                        "name": "assetName"
                    },                    
                    "Signifier": {
                        "name": "assetFullName"
                    },
                    "AssetType": {
                        "name": "assetType",
                        "Id": {
                            "name": "assetTypeId"
                        },
                        "Signifier": {
                            "name": "assetTypeName"
                        }
                    },
                    "Status": {
                        "name": "assetStatus",
                        "Id": {
                            "name": "assetStatusId"
                        },
                        "Signifier": {
                            "name": "assetStatusName"
                        }
                    },
                    "Domain": {
                        "name": "assetDomain",
                        "Id": {
                            "name": "assetDomainId"
                        },
                        "Name": {
                            "name": "assetDomainName"
                        },
                        "Community": {
                            "name": "assetCommunity",
                            "Id": {
                                "name": "assetCommunityId"
                            },
                            "Name": {
                                "name": "assetCommunityName"
                            }
                        }
                    },
                    "StringAttribute": [
                        {
                            "name": "description",
                            "labelId": "00000000-0000-0000-0000-000000003114",
                            "Id": {
                                "name": "descriptionAttributeId"
                            },
                            "LongExpression": {
                                "name": "descriptionAttributeValue"
                            }
                        },
                        {
                            "name": "lastSyncDate",
                            "labelId": "00000000-0000-0000-0000-000000000256",
                            "Id": {
                                "name": "lastSyncDateAttributeId"
                            },
                            "LongExpression": {
                                "name": "lastSyncDateAttributeValue"
                            }
                        }  
                    ],

                    "Relation": [
                        {
                            "name": "fileContainers",
                            "typeId": "00000000-0000-0000-0000-000000007060",
                            "type": "TARGET",
                            "Source": {
                                "name": "fileContainer",          
                                "DisplayName": {
                                    "name": "fileContainerName"
                                },
                                "Id": {
                                    "name": "fileContainerId"
                                }
                            }
                        },
                        {
                            "name": "fileAnnotators",
                            "typeId": "018dacf9-23d7-7cc1-b2a2-aa802ae00f03",
                            "type": "TARGET",
                            "Source": {
                                "name": "fileAnnotator",          
                                "DisplayName": {
                                    "name": "fileAnnotatorName"
                                },
                                "Id": {
                                    "name": "fileAnnotatorId"
                                }
                            }
                        }                        
                    ],
                    "Filter": {
                        "AND": [
                            {
                                "Field": {
                                    "name": "assetCommunityId",
                                    "operator": "IN", 
                                    "values": [community.get("id") for community in communities],
                                    "descendants": "true"
                                }                                
                            },
                            {
                                "Field": {
                                    "name": "assetTypeId",
                                    "operator": "IN", 
                                    "values": [assetType.get("id") for assetType in assetTypes]
                                }                                
                            },
                            {
                                "Field": {
                                    "name": "assetStatusId",
                                    "operator": "IN",
                                    "value": [status.get("id") for status in statuses]
                                }
                            }
                        ]
                    }              
                }
            }
        }
    }
 
    response = collibra.get("session").post(f"{collibra.get('endpoint')}/outputModule/export/json?validationEnabled=false", json=viewConfig)
        
    return response.json().get("view").get("Assets")


# credentials
collibra = {"host": "https://print.collibra.com", "username": "DataLakeAdmin", "password": "W2.Collibra"}

collibra["endpoint"] = f"{collibra['host']}/rest/2.0"


# connect to collibra 
collibra["session"] = requests.Session()

collibra.get("session").auth = HTTPBasicAuth(collibra.get("username"), collibra.get("password"))


# get collibra entity types
assetTypes = {}

response = collibra.get("session").get(f"{collibra.get('endpoint')}/assetTypes")

_=[x(assetTypes, assetType.get("name"), assetType) for assetType in response.json()["results"]] 


# get collibra attribute types
attributeTypes = {}

response = collibra.get("session").get(f"{collibra.get('endpoint')}/attributeTypes")

_=[x(attributeTypes, attributeType.get("name"), attributeType) for attributeType in response.json()["results"]]


# get the collibra relation types
relationTypes = {}

response = collibra.get("session").get(f"{collibra.get('endpoint')}/relationTypes")

_=[x(relationTypes, f"{relationType.get('sourceType').get('name')} {relationType.get('role')} {relationType.get('targetType').get('name')}", relationType) for relationType in response.json()["results"]]


# get collibra statuses types
statuses = {}

response = collibra.get("session").get(f"{collibra.get('endpoint')}/statuses")

_=[x(statuses, status.get("name"), status) for status in response.json()["results"]]


# get collibra communities
communities = {}

response = collibra.get("session").get(f"{collibra.get('endpoint')}/communities")

_=[x(communities, community.get("name"), community) for community in response.json()["results"]]


# get assets dataframe
assets = getAssets(collibra, [communities['Unstructured Data Integrator community']], [assetTypes['File']], [statuses[status] for status in statuses])

df = pd.json_normalize(assets)


# drop asset id
del df['assetId']


# get the asset type name
df['assetType']=df['assetType'].map(lambda x: x[0]['assetTypeName'])


# get the asset status name
df['assetStatus']=df['assetStatus'].map(lambda x: x[0]['assetStatusName'])


# get the asset domain name
df['assetDomain']=df['assetDomain'].map(lambda x: x[0]['assetDomainName'])


# get the asset container name
def t(x, i):
    try:
        return x[0]['fileContainer'][0][i]
    except Exception as e:
        return 'root'

df['fileContainers']=df['fileContainers'].map(lambda x: t(x, 'fileContainerName'))


# get the asset annotators names
def t(x, i):
    try:
        return x['fileAnnotator'][0][i]
    except Exception as e:
        return '-'

df = df.explode('fileAnnotators')

df['fileAnnotators']=df['fileAnnotators'].map(lambda x: t(x, 'fileAnnotatorName'))


# add a few observations
def nobservations(i, c):
    switcher = {
        'isna':c.isna().sum(),
        'isnull':c.isnull().sum(),
        'iszero':(c==0).sum(),
        'distinct':len(c.unique()),
        'dtype':c.dtype.name
    }

    return switcher.get(i,'Invalid')


profile=df.describe(include='all',datetime_is_numeric=True)

profile.fillna('', inplace=True)

for i in ['isna','isnull','iszero','distinct','dtype']:
    r=[]
    
    for j in profile.columns:
        r.append(nobservations(i,df[j]))

    row=pd.DataFrame([r],index=[i],columns=profile.columns)

    profile=profile.append(row)


# page config
st.set_page_config(layout="wide")

style = """
    <style>
        .st-emotion-cache-12w0qpk {
            background-color: #EEEEEE;
            border: 1px solid #DCDCDC;
            padding: 20px;
            border-radius: 10px; 
        }
    
        .st-emotion-cache-1r6slb0 {
            border: 1px solid #DCDCDC;
            padding: 20px;
            border-radius: 10px; 
        }

        .st-emotion-cache-keje6w {
            border: 1px solid #DCDCDC;
            padding: 20px;
            border-radius: 10px; 
        }     

    </style>
"""

#st-emotion-cache-9aoz2h

st.markdown(style, unsafe_allow_html=True)



# general dashboard
st.subheader("General Dashboard")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Scanned data sources", profile['assetDomain']['unique'])

col2.metric("Indexed directories", profile['fileContainers']['unique'])

col3.metric("Files with findings", profile['assetFullName']['unique'])

col4.metric("Annotators found", profile['fileAnnotators']['unique'])


st.subheader("Annotation Summary")

col1, col2, col3 = st.columns(3)

# files per scanned data source
result = df[['assetDomain','assetFullName']].drop_duplicates().groupby(['assetDomain']).count().reset_index().rename(columns={'assetDomain':'data source', 'assetFullName': 'files'}).sort_values(by=['files'], ascending=False)

fig = px.bar(result, x='data source', y='files', title="Files per scanned data source", color='data source', text_auto='.2s', hover_name='data source')

fig.update_traces(textfont_size=8, textangle=0, textposition="outside")

fig.update_layout(height=720, showlegend=False)

fig.update_xaxes(tickangle=0, tickfont=dict(size=10))

fig.update_yaxes(tickangle=0, tickfont=dict(size=10))

col1.plotly_chart(fig, theme="streamlit", use_container_width=True)


# files per indexed directory
result = df[['fileContainers','assetFullName']].drop_duplicates().groupby(['fileContainers']).count().reset_index().rename(columns={'fileContainers':'directory', 'assetFullName': 'files'}).sort_values(by=['files'], ascending=False)

fig = px.bar(result, x='directory', y='files', title="Files per indexed directory", color='directory', text_auto='.2s', hover_name='directory')

fig.update_traces(textfont_size=8, textangle=0, textposition="outside")

fig.update_layout(height=720, showlegend=False)

fig.update_xaxes(tickangle=0, tickfont=dict(size=10))

fig.update_yaxes(tickangle=0, tickfont=dict(size=10))

col2.plotly_chart(fig, theme="streamlit", use_container_width=True)


# files per annotator found
result = df[['fileAnnotators','assetFullName']].drop_duplicates().groupby(['fileAnnotators']).count().reset_index().rename(columns={'fileAnnotators':'annotator', 'assetFullName': 'files'}).sort_values(by=['annotator'], ascending=True)

fig = px.bar(result, x='annotator', y='files', title="Files per annotator found", color='annotator', text_auto='.2s', hover_name='annotator')

fig.update_traces(textfont_size=8, textangle=0, textposition="outside")

fig.update_layout(height=720, showlegend=False)

fig.update_xaxes(tickangle=90, tickfont=dict(size=10))

fig.update_yaxes(tickangle=0, tickfont=dict(size=10))

col3.plotly_chart(fig, theme="streamlit", use_container_width=True)


col1, col2 = st.columns(2)

# files per scanned data source and annotator found
result = df[['assetDomain', 'fileAnnotators', 'assetFullName']].drop_duplicates().groupby(['assetDomain', 'fileAnnotators']).count().reset_index().rename(columns={'assetDomain':'data source', 'fileAnnotators':'annotator', 'assetFullName': 'files'}).sort_values(by=['annotator'], ascending=True)

fig = px.scatter(result, x='annotator', y='data source', size='files', title="Files per scanned data source and annotator found", color='annotator', hover_name='annotator')

fig.update_layout(height=720, showlegend=False)

fig.update_xaxes(tickangle=90, tickfont=dict(size=10))

fig.update_yaxes(tickangle=0, tickfont=dict(size=10))

col1.plotly_chart(fig, theme="streamlit", use_container_width=True)


# files per indexed directory and annotator found
result = df[['fileContainers', 'fileAnnotators', 'assetFullName']].drop_duplicates().groupby(['fileContainers', 'fileAnnotators']).count().reset_index().rename(columns={'fileContainers':'directory', 'fileAnnotators':'annotator', 'assetFullName': 'files'}).sort_values(by=['annotator'], ascending=True)

fig = px.scatter(result, x='annotator', y='directory', size='files', color='annotator', title="Files per indexed directory and annotator found", hover_name='annotator')

fig.update_layout(height=720, showlegend=False)

fig.update_xaxes(tickangle=90, tickfont=dict(size=10))

fig.update_yaxes(tickangle=0, tickfont=dict(size=10))

col2.plotly_chart(fig, theme="streamlit", use_container_width=True)



# get files per annotator
with st.expander("See details"):
    result = df[['assetName', 'fileAnnotators', 'assetFullName']].drop_duplicates().groupby(['assetName', 'fileAnnotators']).count().reset_index().rename(columns={'assetName':'file', 'fileAnnotators':'annotator', 'assetFullName': 'files'}).sort_values(by=['annotator'], ascending=True)

    result['file']=result['file'].map(lambda x: f'{x[0:31]}... ')

    fig = px.scatter(result, x='annotator', y='file', size='files', color='annotator', title="Files per annotator found")

    fig.update_layout(height=2160, showlegend=False)

    fig.update_traces(marker=dict(size=6, symbol="square"))

    fig.update_xaxes(tickangle=90, tickfont=dict(size=10))

    fig.update_yaxes(tickangle=0, tickfont=dict(size=10))

    st.plotly_chart(fig, theme="streamlit", use_container_width=True)


import streamlit.components.v1 as components

# embed streamlit docs in a streamlit app
#components.iframe("https://collibra-demo.dataxray.io/#/i/overview")
