#!/usr/bin/env python

# (c) Dmitry Monakhov dmonakhov@openvz.org

import facebook
import requests
import json
import sys
import os
from optparse import OptionParser

do_verbose = False
do_dryrun = False


def log_err(msg):
        print '[ERR]', msg

def log_info(msg):
        print '[INFO]', msg

class UserCfg:
        def __init__(self, fname):
                self.data = {}
                self.fname = fname
              
        def load_cfg(self):
                global do_verbose
                try:
                        f = open(self.fname, 'r')
                        stub = json.load(f)
                except:
                        if do_verbose:
                                log_info("user config is empty")
                        stub = {}
                for uid in stub:
                        ent = stub[uid];
                        if (('id' not in ent.keys()) or
                            ('name' not in ent.keys()) or
                            ('description' not in ent.keys())):
                                log_err('Fun:load_cfg bad entry');
                                continue
                        self.data[uid] = ent;

        def save_cfg(self):
                if len(self.data) == 0:
                        print "Empty user list, skip"
                        return
                stub = {}
                for uid in self.data:
                        e = {}
                        for name in ['id', 'name', 'description']:
                                e[name] = self.data[uid][name]
                        stub[uid] = e
                with open(self.fname, 'w') as f:
                        json.dump(stub, f, ensure_ascii=False, indent = 4)

        def add(self, uid, name, description):
                e = {}
                e['id'] = uid
                e['name'] = name
                e['description'] = description
                if uid in self.data.keys():
                        log_err("fn:add User %s already exists, ignore" % uid)
                else :
                        self.data[uid] = e
        def delete(self, uid):
                if uid in self.data.keys():
                        del self.data[uid]
                        
def search_comments(graph, users, comments):
        ret = []
        for c in comments:
                if c['from']['id'] in user.keys():
                        ret.append(c)
        return ret

def do_append(lst, post):
        global do_verbose
        if do_verbose:
                log_info("append post id:" + post['id'])
        lst.append(post)
        
def fetch_feed(graph, eid):
        global do_verbose
        lst = []

        if (do_verbose):
                log_info("Try to fetch object " + eid)
        event = graph.get_object(eid)
        posts = graph.get_connections(event['id'], 'feed')
        print "Fetched one"
        # Wrap this block in a while loop so we can keep paginating requests until
        # finished.
        while True:
                try:
	        # Perform some action on each post in the collection we receive from
        	# Facebook.
                        [do_append(lst, post=post) for post in posts['data']]
                        posts = requests.get(posts['paging']['next']).json()
                except KeyError:
                # When there are no more pages (['paging']['next']), break from the
	        # loop and end the script.
                        break
        return lst

def parse_comments(feeds):
        # Return dictionary of comments, key = user_id
        cdict = {}
        for feed in feeds:
                if 'comments' in feed.keys():
                        cdat = feed['comments']['data']
                        for c in cdat:
                                uid = c['from']['id']
                                if uid in cdict.keys():
                                        cdict[uid].append(c)
                                else:
                                        cdict[uid] = [c]
                                
        return cdict

def remove_comments(graph, comments):
        global do_verbose
        removed = 0;

        for c in comments:
                cid = c['id']
                try:
                        if do_verbose:
                                log_info("remove comment id %s" % cid)
                        ret = graph.delete_object(cid)
                        removed = removed + 1
                except Exception as e:
                        log_err("Error while remove_object %s" % cid)
                        print e.__doc__
                        print e.message
                if do_verbose:
                        log_info("remove comment id %s from: %s " %
                                 (cid, c['from']['name']))
        return removed

def main():
        global do_verbose
        global do_dryrun

        usage = "usage: %prog [options] arg"
        parser = OptionParser(usage)
        parser.add_option("-v", "--verbose",
                          action="store_true", dest="verbose")
        parser.add_option("-q", "--quiet",
                          action="store_false", dest="verbose")
        
        parser.add_option("-d", "--dry_run",
                          action="store_true", dest="dryrun",
                          help="Simulation action, without actual execution")

        # Config options
        parser.add_option("-c", "--config", dest="config",
                          help="use config file with name")
        parser.add_option("-I", "--init_config",
                          action="store_true", dest="initconfig",
                          help="Create config file")

        # Initialization options 
        parser.add_option("-i", "--id", dest="event_id",
                          help="Event id")

        parser.add_option("-k", "--keytoken", dest="keytoken",
                          help="FB oauth key token")

        # Cache options
        parser.add_option("-n", "--cachename", dest="cachename",
                          help="Cache file name")

        # Actions 
        parser.add_option("-U", "--update_cache",
                          action="store_true", dest="update_cache",
                          help="Update local cache")
        parser.add_option("-O", "--adduser_by_object", dest="adduser_by_object",
                          help="Add add user by it's object")

        parser.add_option("-A", "--adduser", dest="adduser",
                          help="Add user to black list")

        parser.add_option("-D", "--deluser", dest="deluser",
                          help="Remove user from black list")
        
        parser.add_option("-R", "--rmcomments", 
                          action="store_true", dest="rmcomments",
                          help="Remove all comments from users in blacklist")

        
        (options, args) = parser.parse_args()

        config_name = '.fb_config.json'
        cache_name = 'feed.json'
        user_cfg_name = 'users.json'
        update_cache = False
        if options.config:
                config_name = options.config
        if options.cachename:
                cache_name = option.cachename
        if options.update_cache:
                update_cache = options.update_cache
        if options.verbose:
                do_verbose = options.verbose
        if options.dryrun:
                do_dryrun = options.dryrun
                
        if options.initconfig and ( not options.event_id
                                    or not options.keytoken):
                log_err("--create_config requires --keytoken and --id ")
                parser.print_help()
                return 1

        # Load and parse config files
        try:
                cfgf = open(config_name, 'rw')
                try:
                        cfg = json.load(cfgf)
                except:
                        if not options.initconfig:
                                log_err("Empty config use --create_config")
                                return 1
                        cfg = {}
        except:
                log_err("Can not open config file " + config_name)
                return 1
        
        try:
                feeds_f = open(cache_name, 'rw')
                try:
                        feeds = json.load(feeds_f)
                except:
                        log_info("Bad cache file, force cache update")
                        update_cache = True
        except:
                log_err("Can not open cache file " + cache_name)
                return 1

        try:
                print "init"
                user_cfg = UserCfg(user_cfg_name)
                print "load"
                user_cfg.load_cfg()
        except:
                log_err("Can not open user list file " + user_cfg_name)
                return 1

        if options.event_id:
                cfg['event_id'] = options.event_id
        if options.keytoken:
                cfg['key'] = options.keytoken

        # Config sanity check
        for key in ['key', 'event_id']:
                if key not in cfg.keys():
                        log_err("Bad config: %s is missed" % key)


        if options.initconfig:
                try:
                        print cfg
                        with open(config_name, 'w') as f:
                                json.dump(cfg, f, ensure_ascii=False, indent = 4)
                except:
                        log_err("Can not initialize config file")
                        return 1
        # Actual logic stats here
        # Init face book API
        print "Init Graph : key" + cfg['key']
        graph = facebook.GraphAPI(cfg['key'])
        if (update_cache):
                feeds = fetch_feed(graph, cfg['event_id'])
                with open(cache_name, 'w') as f:
                        json.dump(feeds, f, ensure_ascii=False, indent = 4)
                        f.close()
                
        if options.adduser_by_object:
                try:
                        if do_verbose:
                                log_info ("lookup object: " + options.adduser_by_object)
                        obj = graph.get_object(options.adduser_by_object)
                        options.adduser = obj['from']['id']
                        log_info ("Found obj:%s owner id:%s name:%s" %
                                  ( options.adduser_by_object,
                                    obj['from']['id'], obj['from']['name']))
                except:
                        log_err("adduser_by_object: Object lookup failed")
                        return 1

        if options.adduser:
                try:
                        if do_verbose:
                                log_info ("lookup user_id: " + options.adduser)
                        uobj = graph.get_object(options.adduser)
                except:
                        log_err("adduser: User lockup failed")
                        return 1
                user_cfg.add(uobj['id'], uobj['name'], 'added manually')
                user_cfg.save_cfg()

        if options.deluser:
                user_cfg.add(options.deluser)


        if options.rmcomments:
                found = 0;
                removed = 0
                comm_dict = parse_comments(feeds)
                with open("comments.json", 'w') as f:
                        json.dump(comm_dict, f, ensure_ascii=False, indent = 4)
                
                for uid in user_cfg.data:
                        if do_verbose:
                                log_info("Search uid:" + str(uid))
                        if uid not in comm_dict.keys():
                                if do_verbose:
                                        log_info("No messages found for :" + str(uid))
                                continue
                        num = len(comm_dict[uid])
                        if do_verbose:
                             log_info("Found %d comments for user: %s" % (num, uid))
                        if do_dryrun:
                             continue
                        rm_num = remove_comments(graph, comm_dict[uid])
                        found = found + num
                        removed = removed + rm_num
                print "stats: rmcomments found: " + str(found) + " removed: " + str(removed)

                
if __name__ == "__main__":

        main()
