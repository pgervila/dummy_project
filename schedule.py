# import os, sys
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mesa.time import StagedActivation
from agent import IndepAgent, Young

import numpy as np
import networkx as nx
import random

import copy


class StagedActivationModif(StagedActivation):
    # TODO : add/separate agents by type ??? Is it a good idea ??

    def step(self, pct_threshold=0.9):
        """ Executes all the stages for all agents. """

        for ag in self.agents[:]:
            ag.info['age'] += 1
            for lang in ['L1', 'L12', 'L21', 'L2']:

                #save wc for each agent
                ag.wc_init[lang] = ag.lang_stats[lang]['wc'].copy()

                # update last-time word use vector
                ag.lang_stats[lang]['t'][~ag.day_mask[lang]] += 1
                # set current lang knowledge
                # compute current language knowledge in percentage after 't' update
                if lang in ['L1', 'L12']:
                    real_lang_knowledge = np.maximum(ag.lang_stats['L1']['R'], ag.lang_stats['L12']['R'])
                    ag.lang_stats['L1']['pct'][ag.info['age']] = (np.where(real_lang_knowledge > pct_threshold)[0].shape[0] /
                                                                  len(ag.model.cdf_data['s'][ag.info['age']]))
                else:
                    real_lang_knowledge = np.maximum(ag.lang_stats['L2']['R'], ag.lang_stats['L21']['R'])
                    ag.lang_stats['L2']['pct'][ag.info['age']] = (np.where(real_lang_knowledge > pct_threshold)[0].shape[0] /
                                                                  len(ag.model.cdf_data['s'][ag.info['age']]))
                # reset day mask
                ag.day_mask[lang] = np.zeros(ag.model.vocab_red, dtype=np.bool)
            # Update lang switch
            ag.update_lang_switch()
        if self.shuffle:
            random.shuffle(self.agents)
        # basic IDEA: network adj matrices will be fixed through all stages of one step
        # compute adjacent matrices for family and friends
        Fam_Graph = nx.adjacency_matrix(self.model.nws.family_network,
                                        nodelist=self.agents).toarray()
        self.model.nws.adj_mat_fam_nw = np.nan_to_num(Fam_Graph / Fam_Graph.sum(axis=1, keepdims=True))

        Friend_Graph = nx.adjacency_matrix(self.model.nws.friendship_network,
                                           nodelist=self.agents).toarray()
        self.model.nws.adj_mat_friend_nw = np.nan_to_num(Friend_Graph / Friend_Graph.sum(axis=1, keepdims=True))

        #FG = self.model.nws.adj_mat_friend_nw.copy()

        for stage in self.stage_list:
            for ix_ag, ag in enumerate(self.agents):
                if isinstance(ag, IndepAgent):
                    getattr(ag, stage)(ix_ag)
                else:
                    getattr(ag, stage)()
            if self.shuffle_between_stages:
                random.shuffle(self.agents)
            self.time += self.stage_time

            # print(self.time)
            # if not np.array_equal(FG, self.model.nws.adj_mat_friend_nw):
            #     print('Problem with adjacency MATRIX !!!!!!!!!')
            #     print(np.argwhere(FG != self.model.nws.adj_mat_friend_nw))
            #     mod_ags = np.nonzero(np.invert((FG == self.model.nws.adj_mat_friend_nw).all(axis=1)))[0]
            #     for myag in mod_ags:
            #         # print(self.agents[myag].info)
            #         print(self.agents[myag])
            #         print(self.model.nws.friendship_network[self.agents[myag]])
            #     print('ags lists are same', self.agents == ags_sched)
            # print([ag for ag in self.agents if not self.model.nws.friendship_network[ag]])
            # print('******')
            # print(FG[myag][:10], self.model.nws.adj_mat_friend_nw[myag][:10])

        for ag in self.agents[:]:
            for lang in ['L1', 'L12', 'L21', 'L2']:
                ag.wc_final[lang] = ag.lang_stats[lang]['wc'].copy()

        # check reproduction, death : make shallow copy of agents list,
        # since we are potentially removing agents as we iterate
        for ag in self.agents[:]:
            if isinstance(ag, Young):
                ag.reproduce()
            ag.random_death()
        # loop and update courses in schools and universities year after year
        if not self.steps % self.model.steps_per_year and self.steps:
            for clust_idx, clust_info in self.model.geo.clusters_info.items():
                if 'university' in clust_info:
                    for fac in clust_info['university'].faculties.values():
                        if fac.info['students']:
                            fac.update_courses()
                for school in clust_info['schools']:
                    school.update_courses()
                    if not self.steps % (2 * self.model.steps_per_year):  # every 2 years only, teachers swap
                        school.swap_teachers_courses()
        self.steps += 1

    # @staticmethod
    # def check_ags_lang_change(l_init, l_post):
    #     init_lang_labels = set([(ag.unique_id, ag.info['language']) for ag in l_init])
    #     post_lang_labels = set([(ag.unique_id, ag.info['language']) for ag in l_post])
    #
    #     return post_lang_labels.difference(init_lang_labels)


    def replace_agent(self, old_agent, new_agent):
        ix_in_schedule = self.model.schedule.agents.index(old_agent)
        self.model.schedule.remove(old_agent)
        self.model.schedule.agents.insert(ix_in_schedule, new_agent)

