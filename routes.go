/**
* Copyright © 2017, ACM@UIUC
*
* This file is part of the ACM GPU Cluster Project.
*
* The ACM GPU Cluster Project is open source software, released under
* the University of Illinois/NCSA Open Source License. You should have
* received a copy of this license in a file with the distribution.
**/

package routes

import (
	"net/http"

	"github.com/acm-uiuc/gpu-cluster-backend/dockermngr"
)

type Route struct {
	Name        string           `json:"Name"`
	Method      string           `json:"Method"`
	Pattern     string           `json:"Pattern"`
	HandlerFunc http.HandlerFunc `json:"Handler"`
}

type RouteCollection []Route

//API Interface
var APIRoutes = RouteCollection{
	Route{
		"GetEvents",
		"GET",
		"/events",
		GetEvents,
	},
	Route{
		"GetUpcomingEvents",
		"GET",
		"/events/upcoming",
		GetUpcomingEvents,
	},
}

// arbor.Route handler
func GetEvents(w http.ResponseWriter, r *http.Request) {
	arbor.GET(w, EventsURL+r.URL.String(), EventsFormat, "", r)
}

func GetUpcomingEvents(w http.ResponseWriter, r *http.Request) {
	arbor.GET(w, EventsURL+r.URL.String(), EventsFormat, "", r)
}